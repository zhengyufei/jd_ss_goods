docker rm -f jd-ss-goods

docker run -it --restart=always -d --net=host --name jd-ss-goods \
        -v /opt/gopath/src/gitlab.xiaoduoai.com/ecrobot/jd-ss-goods:/root/projects/xiaoduo/jd-ss-goods/ \
        -v /etc/localtime:/etc/localtime \
        -v /var/log/xiaoduo:/var/log/xiaoduo \
        -w /root/projects/xiaoduo/jd-ss-goods \
        -e LANG="en_US.UTF-8" \
        hub.xiaoduotech.com/python3.5.0:base /root/.pyenv/versions/3.5.0/bin/python main.py -c ../config/config.json
