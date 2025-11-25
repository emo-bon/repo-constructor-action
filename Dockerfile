FROM python:3.9
COPY entrypoint.sh /opt/entrypoint.sh
COPY action.py /opt/action.py
COPY requirements.txt /opt/requirements.txt
COPY workflow_template.yml /opt/workflow_template.yml
RUN chmod +x /opt/entrypoint.sh
RUN python -m pip install -r /opt/requirements.txt
ENTRYPOINT ["/opt/entrypoint.sh"]
