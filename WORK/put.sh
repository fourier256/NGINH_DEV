#!/bin/bash

# SFTP 서버 접속 정보
HOST="3.38.181.233"
USER="ubuntu"
PASS="your_password"
REMOTE_DIR="WORK/"
LOCAL_DIR="your_local_directory"

# SFTP 명령어 자동화
sftp -oBatchMode=no -i ./MY_EC2_KEY.pem -b - $USER@$HOST <<EOF
cd $REMOTE_DIR
mput -r *
exit
EOF

echo "파일 업로드 완료"