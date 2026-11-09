"""Run one lab command in a real Windows console and capture its window."""
import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import subprocess
import sys
import time
from PIL import ImageGrab

ROOT = Path(__file__).resolve().parent


def main():
    label = sys.argv[1]
    args = json.loads(sys.argv[2])
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    user = ctypes.WinDLL('user32', use_last_error=True)
    user.SetProcessDPIAware()
    kernel.GetConsoleWindow.restype = wintypes.HWND
    hwnd = kernel.GetConsoleWindow()
    if not hwnd:
        raise RuntimeError('A real console window is required')
    kernel.SetConsoleTitleW('lab9_Omar_Khalil - ' + label)
    class Coord(ctypes.Structure):
        _fields_ = [('X', ctypes.c_short), ('Y', ctypes.c_short)]
    class Font(ctypes.Structure):
        _fields_ = [('cbSize', wintypes.ULONG), ('nFont', wintypes.DWORD),
                    ('dwFontSize', Coord), ('FontFamily', wintypes.UINT),
                    ('FontWeight', wintypes.UINT), ('FaceName', wintypes.WCHAR * 32)]
    kernel.GetStdHandle.restype = wintypes.HANDLE
    font = Font()
    font.cbSize = ctypes.sizeof(font)
    font.dwFontSize = Coord(0, 14)
    font.FontWeight = 400
    font.FaceName = 'Consolas'
    kernel.SetCurrentConsoleFontEx(kernel.GetStdHandle(-11), False, ctypes.byref(font))
    subprocess.run(['cmd.exe', '/c', 'mode con: cols=132 lines=30'], stdout=subprocess.DEVNULL)
    user.ShowWindow(hwnd, 5)
    user.SetWindowPos(hwnd, None, 10, 10, 0, 0, 5)
    user.SetForegroundWindow(hwnd)
    print('lab9_Omar_Khalil | Omar Khalil', flush=True)
    print('PS ' + str(ROOT) + '> ' + subprocess.list2cmdline(['python', *args]), flush=True)
    result = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True)
    output = result.stdout + result.stderr
    (ROOT/'reports'/f'{label}.txt').write_text(
        'Project: lab9_Omar_Khalil\nPS ' + str(ROOT) + '> ' +
        subprocess.list2cmdline(['python', *args]) + '\n\n' + output, encoding='utf-8')
    lines = output.rstrip().splitlines()
    chunks = [lines[i:i+20] for i in range(0, len(lines), 20)] or [[]]
    captures = []
    for page, chunk in enumerate(chunks, 1):
        subprocess.run(['cmd.exe', '/c', 'cls'])
        print(f'lab9_Omar_Khalil | Omar Khalil | Output page {page}/{len(chunks)}', flush=True)
        print('PS ' + str(ROOT) + '> ' + subprocess.list2cmdline(['python', *args]), flush=True)
        print('\n'.join(chunk), flush=True)
        print('\nExit code: ' + str(result.returncode), flush=True)
        user.SetForegroundWindow(hwnd)
        time.sleep(1)
        rect = wintypes.RECT()
        user.GetWindowRect(hwnd, ctypes.byref(rect))
        # DWM bounds exclude the invisible resize margin around the window.
        dwm = ctypes.WinDLL('dwmapi')
        dwm.DwmGetWindowAttribute(hwnd, 9, ctypes.byref(rect), ctypes.sizeof(rect))
        dest = ROOT/'reports'/f'{label}_{page}.png'
        ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom)).save(dest)
        captures.append(dest.name)
    (ROOT/'reports'/f'{label}.capture.json').write_text(json.dumps({
        'method': 'Actual Windows console window captured with ImageGrab',
        'command': [sys.executable, *args], 'returncode': result.returncode,
        'images': captures,
        'window_rect': [rect.left, rect.top, rect.right, rect.bottom],
    }, indent=2), encoding='utf-8')
    if result.returncode:
        raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
