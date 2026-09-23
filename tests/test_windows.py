"""Regression coverage for microphone failures and tray recovery."""
import sys
import unittest
from unittest.mock import Mock, patch


@unittest.skipUnless(sys.platform == "win32", "Windows backend")
class WindowsTests(unittest.TestCase):
    def test_microphone_errors_propagate_and_release_com(self):
        from win_mic_control import MicControl
        for operation in (MicControl().is_muted, MicControl().toggle,
                          lambda: MicControl().set_mute(True)):
            with self.subTest(operation=operation), \
                 patch("win_mic_control._get_mic_volume", side_effect=RuntimeError("disconnected")), \
                 patch("win_mic_control.comtypes.CoInitialize"), \
                 patch("win_mic_control.comtypes.CoUninitialize") as release:
                with self.assertRaisesRegex(RuntimeError, "disconnected"):
                    operation()
                release.assert_called_once()

    def test_poll_tracks_external_mute_and_reconnect(self):
        from win_tray_app import TrayApp
        app = TrayApp.__new__(TrayApp)
        app._root = Mock()
        app._mic = Mock()
        app._mic.is_muted.side_effect = [False, True, RuntimeError("unplugged"), False]
        app._last_status = None
        app._update_icon = Mock()
        for available, muted in [(True, False), (True, True), (False, True), (True, False)]:
            app._poll_microphone()
            self.assertEqual((app._mic_available, app._muted), (available, muted))
        self.assertEqual(app._update_icon.call_count, 4)
        self.assertEqual(app._root.after.call_count, 4)

    def test_frozen_config_lives_beside_executable(self):
        import config_manager
        with patch.object(sys, "frozen", True, create=True), \
             patch.object(sys, "executable", r"C:\Apps\MicMuteTray.exe"):
            self.assertEqual(config_manager._default_config_file(), r"C:\Apps\config.json")


if __name__ == "__main__":
    unittest.main()
