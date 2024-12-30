from weasyprint import HTML
import matplotlib.pyplot as plt
import pandas as pd
import os
import json

from loguru import logger


class ReportGenerator:

    def __init__(self, client):
        self.client = client

    def generate_report(self, analysis, tables, agent, schema):
        logger.info("Starting to generate the report")

