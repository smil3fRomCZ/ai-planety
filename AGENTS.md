# Repository Guidelines

## Project Structure & Module Organization

`index.html` contains the entire Czech-language space explorer: HTML controls, inline CSS, an import map, and a JavaScript module. The module groups planet configuration, scene construction, generated effects, speech, navigation, and animation into commented sections. Extend the relevant section and reuse `registerTarget()` for navigable objects.

Three.js and OrbitControls load from unpkg; planet textures load from jsDelivr. Other visuals are generated in code. There are no separate source, asset, or test directories. `.claude/settings.local.json` contains local tooling configuration.

## Build, Test, and Development Commands

No package installation, compilation, or build step is configured.

- `Start-Process ./index.html`: open the app directly from PowerShell for a quick preview.
- `python -m http.server 8000 --bind 127.0.0.1`: serve the directory locally if Python is installed; open `http://localhost:8000` in a browser.

Use a browser with WebGL and import-map support. Internet access is needed for CDN modules and textures. Reload after edits; there is no development watcher.

## Coding Style & Naming Conventions

Follow the existing two-space indentation in CSS and JavaScript. Use semicolons, single-quoted JavaScript strings, `const` by default, and `let` for reassigned values. Use camelCase for functions and variables (`createStarfield`, `bodyMap`), uppercase names for configuration constants (`BODIES`, `HOME_POS`), and existing hyphenated CSS classes (`planet-btn`).

Preserve UTF-8 encoding, Czech interface text, and descriptive section comments. Keep changes focused; no formatter or linter is configured.

## Testing Guidelines

There is no automated framework, test naming convention, or coverage threshold. Verify changes manually:

- Confirm the scene renders and the loading overlay disappears.
- Select planets and special objects; check labels, camera travel, and target tracking.
- Exercise scene clicks, drag, zoom, and the home button.
- Resize to narrow and wide viewports; inspect controls and browser console errors.
- Check spoken names when speech synthesis is available and texture fallbacks when applicable.

## Commit & Pull Request Guidelines

This checkout has no Git metadata, so historical commit conventions cannot be verified. Use concise imperative subjects, such as `Fix camera tracking after planet selection`.

For pull requests, describe the behavior changed, link relevant issues, and record manual checks and browser used. Include screenshots or a short recording for visual or animation changes.
