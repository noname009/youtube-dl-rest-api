FROM python:3-onbuild

RUN apt-get update && \
     apt-get install -y libav-tools vim && \
     rm -rf /var/lib/apt/lists/*

COPY ./run.sh /
COPY ./youtube-dl-rest-api-server.py /
COPY ./youtube-dl-update.py /
COPY ./BugsTagger.py /
COPY ./downfolder /

RUN ln -s /usr/src/app/downfolder /

EXPOSE 4287

ENV MY_ID yotubeapi
ENV MY_PW yotubeapi
ENV MY_SC_TIME 06:30
ENV MY_LANG ko
ENV TZ=Asia/Seoul

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

VOLUME ["/downfolder"]

CMD [ "/bin/bash", "/run.sh" ]