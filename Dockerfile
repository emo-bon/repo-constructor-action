FROM python:3.9
RUN pip install pygithub pandas
COPY action.py /opt/action.py
COPY entrypoint.sh /opt/entrypoint.sh
ENTRYPOINT ["/opt/entrypoint.sh"]
