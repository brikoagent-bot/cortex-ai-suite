FROM python:3.11-slim
WORKDIR /app

# Install all requirements
COPY seo-audit/requirements.txt /tmp/req1.txt
COPY sales-intel/requirements.txt /tmp/req2.txt
COPY vc-diligence/requirements.txt /tmp/req3.txt
RUN pip install --no-cache-dir -r /tmp/req1.txt -r /tmp/req2.txt -r /tmp/req3.txt

# Copy all apps
COPY seo-audit/ /app/seo-audit/
COPY sales-intel/ /app/sales-intel/
COPY vc-diligence/ /app/vc-diligence/

# Copy launcher
COPY launcher.py /app/launcher.py

EXPOSE 8501
CMD ["streamlit", "run", "launcher.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
