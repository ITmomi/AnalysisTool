# MPA Analysis Tool Frontend

# 開発バージョン
- Nodeバージョン : v14.16.0
- yarnバージョン : v1.22.5
- reactバージョン : v17.0.1

# 開発環境構成
## パッケージ設置
1. ソースをCloneする。
2. IntelliJを開いてfrontフォルダをWorkspaceに指定してOpenする。
3. コマンドウィンドウで`yarn`コマンドを入力して必要パッケージを設置する。

> Error: unable to verify the first certificate

のようなエラー発生時、`set NODE_TLS_REJECT_UNAUTHORIZED=0`を入力して再び設置する。

Timeout発生時、`yarn install --network-timeout 600000`を実行する。


## 実行スクリプト
1. `yarn start` : 開発モード
2. `yarn build` : 'back/web/static'フォルダにリリース用パッケージングjsファイルが生成
 
## IntelliJ 設定適用
http://10.1.9.22:9080/product/mpaanalysistool/wikis/Settings/IntelliJ/ESLint-Prettier 참고
