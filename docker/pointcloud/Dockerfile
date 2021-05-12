FROM intelvcl/open3d-test:18.04-deps-mc3

WORKDIR /home
COPY entrypoint.sh .
COPY calculate_pointcloud.py .

ENTRYPOINT ["/home/entrypoint.sh"]

