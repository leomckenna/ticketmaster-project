# Use an official Python image
FROM python:3.13

# Set working directory
WORKDIR /app

# Copy your code and requirements
COPY . /app

# Install dependencies including Jupyter
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install jupyter

# Expose Jupyter's default port
EXPOSE 8888

# Start Jupyter Notebook server
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
