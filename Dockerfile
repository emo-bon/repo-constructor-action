FROM python:3.9
RUN pip install pygithub pandas
COPY action.py /action.py
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
