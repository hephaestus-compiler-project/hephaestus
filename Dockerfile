FROM ubuntu

RUN apt update -yqq && apt upgrade -yqq
RUN apt install curl unzip zip default-jre default-jdk -yqq
RUN rm /bin/sh && ln -s /bin/bash /bin/sh
RUN curl -s https://get.sdkman.io | /bin/bash
RUN chmod a+x "/root/.sdkman/bin/sdkman-init.sh"
RUN source "/root/.sdkman/bin/sdkman-init.sh" && \
    sdk install kotlin 1.4.21  && \
    sdk install kotlin 1.4.20  && \
    sdk install kotlin 1.4.10  && \
    sdk install kotlin 1.4.0   && \
    sdk install kotlin 1.3.72  && \
    sdk install kotlin 1.3.71  && \
    sdk install kotlin 1.3.70  && \
    sdk install kotlin 1.3.61  && \
    sdk install kotlin 1.3.60  && \
    sdk install kotlin 1.3.50  && \
    sdk install kotlin 1.3.41  && \
    sdk install kotlin 1.3.40  && \
    sdk install kotlin 1.3.31  && \
    sdk install kotlin 1.3.30  && \
    sdk install kotlin 1.3.21  && \
    sdk install kotlin 1.3.20  && \
    sdk install kotlin 1.3.11  && \
    sdk install kotlin 1.3.10  && \
    sdk install kotlin 1.3.0   && \
    sdk install kotlin 1.2.71  && \
    sdk install kotlin 1.2.70  && \
    sdk install kotlin 1.2.61  && \
    sdk install kotlin 1.2.60  && \
    sdk install kotlin 1.2.51  && \
    sdk install kotlin 1.2.50  && \
    sdk install kotlin 1.2.41  && \
    sdk install kotlin 1.2.40  && \
    sdk install kotlin 1.2.31  && \
    sdk install kotlin 1.2.30  && \
    sdk install kotlin 1.2.21  && \
    sdk install kotlin 1.2.20  && \
    sdk install kotlin 1.2.10  && \
    sdk install kotlin 1.2.0   && \
    sdk install kotlin 1.1.61  && \
    sdk install kotlin 1.1.60  && \
    sdk install kotlin 1.1.51  && \
    sdk install kotlin 1.1.50  && \
    sdk install kotlin 1.1.4-3 && \
    sdk install kotlin 1.1.4-2 && \
    sdk install kotlin 1.1.4   && \
    sdk install kotlin 1.1.3-2 && \
    sdk install kotlin 1.1.3   && \
    sdk install kotlin 1.1.2-5 && \
    sdk install kotlin 1.1.2-2 && \
    sdk install kotlin 1.1.2   && \
    sdk install kotlin 1.1.1   && \
    sdk install kotlin 1.1     && \
    sdk install kotlin 1.0.7   && \
    sdk install kotlin 1.0.6   && \
    sdk install kotlin 1.0.5-2 && \
    sdk install kotlin 1.0.5   && \
    sdk install kotlin 1.0.4   && \
    sdk install kotlin 1.0.3   && \
    sdk install kotlin 1.0.2   && \
    sdk install kotlin 1.0.1-2 && \
    sdk install kotlin 1.0.1-1 && \
    sdk install kotlin 1.0.1   && \
    sdk install kotlin 1.0.0
COPY ./main.py main.py
COPY ./src src
# To change version run `sdk use kotlin 1.3.50`
