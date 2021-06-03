# ST3S
Speech-To-Text-To-Speech
Turns your voice to text then back to speech

## Usage:
You will be prompted to: select a hotkey, select a TTS voice, Word Rate, Input Device, Output Device.
Using the hotkey will record your voice, then it will be processed, and output from the selected output device.
Ctrl + C will reset the process.

For intended use, a Virtual Audio Cable should be used to route the generated voice into a virtual "input" cable.
VB-Audio has free to use software, including Virtual Audio Cables and mixers (Voicemeeter). This is the software that is suggested to be used.

The "Input Device" you select should be your microphone.
The "Output Device" should be the Virtual Audio Cable.
In Windows or your intended program, you can then select the Virtual Audio Cable as the input device.
The generated audio will then play as an input into Windows or your intended program (Discord, Skype, Teamspeak, etc.)

## Compile:
``pyinstaller.exe --name ST3S --onefile -i 'icon.ico' sttts.py``

## Additional Voices:
Windows 10 has the option to use several different TTS voices, as well as download others through the Narrator Settings panel.
Only a few of these are available to 3rd Party Programs, including this one. Registry edits must be made to enable these voices for use.
The regedits folder contains registry edits that enable these additional voices, though only Eva (Cortana) and Mark are installed in Windows 10 by default.
To use the additional voices, one must go to Settings > Time & Language > Speech > Manage voices > (Check all English voices).
Only English voices are supported.
