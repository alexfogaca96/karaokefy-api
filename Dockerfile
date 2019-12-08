FROM continuumio/miniconda:latest

WORKDIR /home/karaokefy-api/

COPY boot.sh ./
COPY environment.yml ./
COPY src/ ./src/

RUN chmod +x boot.sh

ENV PATH /root/anaconda3/bin:$PATH
RUN conda update conda && \
    conda env create -f environment.yml && \
    echo "source activate karaokefy-api" > ~/.bashrc
ENV PATH /opt/conda/envs/karaokefy-api/bin:$PATH

EXPOSE 5000

ENTRYPOINT ["./boot.sh"]