# ProExtractor

ProExtractor imports legacy binary ProPresenter `.pro` song files into a local
SQLite database and exports the reconstructed song text in the default
arrangement order.

It is intended for local library processing: the application code can be shared
openly, while your imported song database and exported lyrics stay outside source
control.

Created by OpenAI Codex in collaboration with laslingerland.

## Features

- Import one `.pro` file or a directory of `.pro` files.
- Store imported songs in SQLite.
- List and search imported songs.
- Export one song to text, CSV, or JSON.
- Export all songs in the database to a directory.
- Inspect a `.pro` file with parser diagnostics.
- Keep ProPresenter parsing behind an adapter, so future importers can be added
  without changing the domain, use cases, repository, exporters, or CLI behavior.

## Project status

ProExtractor currently targets legacy binary ProPresenter `.pro` files. These
files are not a stable public interchange format, so the importer uses recovered
strings, UUIDs, RTF blocks, section labels, and inferred relationships.

Use `proextractor inspect SOURCE --debug` when validating a new library or when a
song does not import as expected.

## Installation

Requirements:

- Python 3.12 or newer

### Linux

On Debian/Ubuntu-like systems, install Python and venv support first:

```sh
sudo apt update
sudo apt install python3 python3-venv
```

If your distribution ships Python older than 3.12, install Python 3.12 or newer
through your distribution packages, `pyenv`, or another trusted Python source.

Then install ProExtractor from the project directory:

```sh
./install.sh
```

The Linux installer creates a project-local virtual environment in `.venv/`,
installs the package in editable mode, and links the `proextractor` command into
`~/.local/bin`. It avoids system-wide `pip install`, so it works with
PEP 668 externally managed Python installations.

If `~/.local/bin` is not on your `PATH`, either add it to your shell
configuration or run the linked command directly:

```sh
~/.local/bin/proextractor --help
```

Uninstall on Linux:

```sh
./uninstall.sh
```

Uninstalling does not delete your database or source files. If the default
database exists, the uninstall script prints its location.

### macOS

Install Python 3.12 or newer. With Homebrew:

```sh
brew install python
```

Then create a virtual environment and install ProExtractor:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
proextractor --help
```

If you want a shell-wide command, keep using the virtual environment when running
ProExtractor or add a small shell alias, for example:

```sh
alias proextractor="$PWD/.venv/bin/proextractor"
```

### Windows

Install Python 3.12 or newer from the Microsoft Store or from
https://www.python.org/downloads/windows/. During installation, enable the option
to add Python to `PATH`.

In PowerShell, from the project directory:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
proextractor --help
```

If PowerShell blocks activation scripts, either allow local scripts for your user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

or run ProExtractor directly:

```powershell
.\.venv\Scripts\proextractor.exe --help
```

## Database location

By default, ProExtractor stores imported songs here:

```text
data/songs.sqlite
```

The `data/` directory is ignored by Git. This keeps local song data, imported
lyrics, translations, and other generated database content out of source control.

You can override the database path per command with `--sqlite`:

```sh
proextractor list --sqlite ./other.sqlite
```

## Usage

Show the full CLI help:

```sh
proextractor --help
```

Import a single file:

```sh
proextractor import song.pro
```

Import a directory recursively:

```sh
proextractor import ./library
```

List imported songs:

```sh
proextractor list
```

Search titles, lyrics, and translations:

```sh
proextractor search "worthy"
```

Export one song to the terminal:

```sh
proextractor export 1 --format txt
```

Export one song to a file:

```sh
proextractor export 1 --format txt --output song.txt
proextractor export "No One Like The Lord" --format json --output song.json
```

Export all songs to a directory:

```sh
proextractor export --all --format txt --output-dir ./exports
```

Inspect a source file without importing it:

```sh
proextractor inspect song.pro
proextractor inspect song.pro --debug
```

## Import behavior

Song titles are taken from the `.pro` filename.

Files without recognizable song sections are skipped during directory imports.
This avoids importing generic slides, media items, and other non-song documents
as songs.

Reimporting the same ProPresenter source ID updates the existing database record
instead of creating a duplicate. If different source files have the same title,
the repository stores them as:

```text
Title
Title (1)
Title (2)
```

## Export formats

Text export produces a readable song layout grouped by section:

```text
[Verse]

There is One on the throne
Er is er Eén op de troon
```

CSV export contains:

```text
section,slide_index,sung_text,translation
```

JSON export contains structured song data including sections, slides, and
arrangements.

## Architecture

ProExtractor uses Clean Architecture / Ports & Adapters.

```text
proextractor/
  domain/          pure domain models
  application/     use cases and port protocols
  adapters/        ProPresenter, SQLite, and exporter implementations
  cli/             command-line wiring
```

Dependency direction:

- Domain depends on nothing.
- Application depends on domain models and port protocols.
- Adapters depend on application and domain.
- CLI wires concrete adapters into use cases.

The ProPresenter binary parsing code lives in:

```text
proextractor/adapters/propresenter/
```

SQLite persistence lives in:

```text
proextractor/adapters/sqlite/
```

Export formatting lives in:

```text
proextractor/adapters/exporters/
```

This separation is intentional. If the ProPresenter format changes, a new
importer adapter should be enough; the domain model, use cases, repository,
exporters, and CLI semantics should remain stable.

## Development

Install test dependencies in the project virtual environment:

```sh
.venv/bin/python -m pip install -e '.[test]'
```

Run tests:

```sh
.venv/bin/python -m pytest
```

Run the package without installing the shell command:

```sh
python -m proextractor --help
```

## Data, copyright, and privacy

This repository should contain application source code, tests, schema files, and
documentation only.

Do not commit:

- `data/`
- `*.sqlite`, `*.sqlite3`, or `*.db`
- imported ProPresenter libraries
- exported song lyric collections

Those files may contain copyrighted lyrics, translations, private planning data,
or church library content. Keep them local unless you have explicit permission to
share them.

## License

ProExtractor is released under the MIT License. See [LICENSE](LICENSE).
