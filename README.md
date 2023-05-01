## SteelSeries Battery Indicator
### Description
This python program provides SteelSeries wireless mouse owners with a simple way to see their current battery status. The battery status is shown as a tray icon, furthermore there is a visual and auditory alert whenever the battery drops beneath 15%.

### Installation
Go to [releases](https://github.com/nicholasdehnen/ss-battery-indicator/releases) and get the latest `battery_indicator_setup.exe`. This installer will automatically place the program into auto-start.

### Open issues, todo, etc.
This app is very basic right now, but works.

Issues:
- `rivalcfg` sometimes returns either 630% or -5% battery charge.
  This is currently ignored and retried, however there should probably be an upper limit for the number of retries.

Future improvements:
- Add GUI to make sounds, alert level and other stuff configurable
- Find a nicer icon
- ...

### Credits
This project is largely based on [rivalcfg](https://github.com/flozz/rivalcfg).
