## 1. SAM install
```
wget https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip
sha256sum aws-sam-cli-linux-x86_64.zip
unzip aws-sam-cli-linux-x86_64.zip -d sam-installation
sudo ./sam-installation/install
sam --version
```

## 2. SAM deploy
```
sam build --use-container
sam deploy
```
`--use-container` option을 사용하면, 빌드에 필요한 툴이 컨테이너에 포함되어 있기 때문에 로컬에 툴을 설치하지 않아도 됩니다.
