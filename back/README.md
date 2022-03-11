# MPA Analysis Tool Backend

# 開発バージョン
- pythonバージョン : 3.9.4
- PostgreSQL : 10.16

# 開発環境構成
## Python設置
1. C:\Python39フォルダにPythonを設置する。

## inno setup設置
1. C:\Program Files (x86)\Inno Setup 6フォルダにinno setupを設置する。

## Pythonパッケージ設置
1. ソースをCloneする。
2. Pycharmを開いてbackフォルダをWorkspaceに指定してOpenする。
3. Pycharmで仮想環境(venv)を設定する。
4. Pycharmコマンドウィンドウでパッケージ設置命令語を入力する。

`pip install --trusted-host files.pythonhosted.org -r requirements.txt`

## Flask App 実行方法
Terminalの/back/フォルダ経路で下記を実行

- 開発用で実行

`python main.py`

- リリース用で実行

`python main.py release` 

# ユニットテスト 
1. pytest, pytest-watchパッケージ設置

`pip install --trusted-host files.pythonhosted.org pytest pytest-watch`
   
2. Terminalで`ptw`を実行すれば、コード修正の時ごとに自動で/testフォルダのtestcaseが実行される。 

# pytestを利用したcoverageテスト
1. pytest-covパッケージ設置

`pip install --trusted-host files.pythonhosted.org pytest-cov`

2. /backフォルダ経路に.coveragercファイルを生成。内容はなくても関係ない。

3. pytestテスト命令実施

`pytest -s -vv --cov=common --cov=controller --cov=dao --cov=flaskapp --cov=service --cov-report=html test/`

* -s : printログ表示
* -vv : Test Case別テスト結果確認。エラー時Fullログを表示。
* --cov-append : 以前のカバレッジテスト結果に加えてテスト実施。

# requirements.txtにpackage追加方法
Pythonパッケージ追加する時は、

`pip install --trusted-host files.pythonhosted.org パッケージ名`

で個別設置後、

`pip freeze > requirements.txt`

を実行してrequirements.txtファイルに反映してください。

# メモリリクテスト方法
1. memory_profilerパッケージ設置、matplotlibパッケージ設置(結果グラフ生成用)

`pip install --trusted-host files.pythonhosted.org memory_profiler matplotlib`

2. 下記の命令実行

`mprof run --include-children main.py`

* --include-children : subprocessのメモリー使用量をmainに含んで表示。

3. 結果グラフ確認

`mprof plot` 

# ライセンス抽出
## Python
1. pip-licensesパッケージ設置

`pip install --trusted-host files.pythonhosted.org pip-licenses`

2. venv環境で下記のコマンドを実行

`pip-licenses --with-urls --format=markdown`

## React
1. license-checkerパッケージ設置

`npm install -g license-checker`

2. front環境で下記のコマンドを実行

`license-checker --production --csv --out license_production.csv`

## Installer Build
1. Python設置
`C:\Python39`フォルダにPythonを設置する。

2. pip Upgrade
Terminalを管理者モードで実行後`C:\Python39\Scripts\`に移動後下記のcommandを実行。

`pip install --trusted-host files.pythonhosted.org --upgrade pip`

3. virtualenv設置

`pip install --trusted-host files.pythonhosted.org virtualenv`

4. Make.bat実行
/backフォルダのMake.batを実行する。

- yarn build중 메모리에러 발생 시

> 92% sealing asset processing TerserPlugin
> <--- Last few GCs --->
> 
> [6960:000001B2E7503890]   121694 ms: Mark-sweep (reduce) 1016.7 (1026.6) -> 1015.9 (1027.8) MB, 1857.1 / 0.0 ms  (average mu = 0.081, current mu = 0.002) allocation failure scavenge might not succeed
> [6960:000001B2E7503890]   124237 ms: Mark-sweep (reduce) 1017.0 (1026.8) -> 1016.3 (1028.1) MB, 2538.1 / 0.0 ms  (average mu = 0.037, current mu = 0.002) allocation failure scavenge might not succeed
> 
> 
> <--- JS stacktrace --->
> 
> FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed - JavaScript heap out of memory
> 1: 00007FF6C875052F napi_wrap+109311
> 2: 00007FF6C86F5256 v8::internal::OrderedHashTable<v8::internal::OrderedHashSet,1>::NumberOfElementsOffset+33302
> 3: 00007FF6C86F6026 node::OnFatalError+294
> 4: 00007FF6C8FC163E v8::Isolate::ReportExternalAllocationLimitReached+94
> 5: 00007FF6C8FA64BD v8::SharedArrayBuffer::Externalize+781
> 6: 00007FF6C8E5094C v8::internal::Heap::EphemeronKeyWriteBarrierFromCode+1516
> 7: 00007FF6C8E5BC8A v8::internal::Heap::ProtectUnprotectedMemoryChunks+1258
> 8: 00007FF6C8E58E39 v8::internal::Heap::PageFlagsAreConsistent+2457
> 9: 00007FF6C8E4DA61 v8::internal::Heap::CollectGarbage+2033
>10: 00007FF6C8E4BC65 v8::internal::Heap::AllocateExternalBackingStore+1317
>11: 00007FF6C8E6C057 v8::internal::Factory::NewFillerObject+183
>12: 00007FF6C8B9C0B1 v8::internal::interpreter::JumpTableTargetOffsets::iterator::operator=+1409
>13: 00007FF6C9049FED v8::internal::SetupIsolateDelegate::SetupHeap+463949
>14: 000002C6304F2571
>error Command failed with exit code 134.
>info Visit https://yarnpkg.com/en/docs/cli/run for documentation about this command.

\front\package.json파일의 build 스크립트를 하기와 같이 변경.
```jason
{
    "scripts": {
        "build": "node --max-old-space-size=8192 node_modules/webpack/bin/webpack.js --progress --mode=production",
        ...
    }
}
```

5. Installer生成位置

`/back/dist`フォルダにinstaller(MPA Analysis Tool_x.x.x_installer_x64.exe file)が生成される。

# Database Migration
## Package Install
Install `alembic` package using the command below

`pip install --trusted-host files.pythonhosted.org alembic`

## Create revision
`alembic revision -m "v1_0_0"`

## Database Upgrade
`alembic upgrade <revision>`

## Database Downgrade
`alembic downgrade <revision>`