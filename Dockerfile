FROM python:3.9
RUN pip install pygithub pandas
COPY github_client.py /github_client.py
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
