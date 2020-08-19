# XCAssetsOptim

XCAssetsOptim is a set of Python scripts that help optimize asset catalogs (`.xcassets`) in Xcode projects.

## 1. App Icons Optimization

`appiconset_optim.py` can optimize app iconset (`.appiconset`) in asset catalogs.

- Fulfill app iconsets with all `size`s of `idiom`s and `scale`s. Even if only one 1024px icon is provided.

- Clean up the naming of app icons.

- Check and fix Xcode warnings and errors in app iconsets.

- Check and fix issues in application submission, like: 

  - Error ITMS-90717: "Invalid App Store Icon. The App Store Icon in the asset catalog in 'YourApp.app' can't be transparent nor contain an alpha channel."

- Optimize and compress app icons. (Requires [ImageOptim](https://imageoptim.com/mac) installed)

### Quickstart

Perform the following command with `python3` :

```bash
$ python3 path/to/appiconset_optim.py path/to/appiconset
```

Or the following shorter command if you have given an execute permission (`x`) to `appiconset_optim.py` :

```bash
$ path/to/appiconset_optim.py path/to/appiconset
```
