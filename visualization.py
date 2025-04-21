import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import pandas as pd
import plotly.express as px

def plot_similarity_heatmap(similarity_list, file_count):
    """Generates a base64-encoded heatmap image of file similarities."""
    matrix = [[0] * file_count for _ in range(file_count)]
    for sim in similarity_list:
        i = int(sim['File 1'].split()[-1]) - 1
        j = int(sim['File 2'].split()[-1]) - 1
        matrix[i][j] = sim['Similarity']
        matrix[j][i] = sim['Similarity']

    df = pd.DataFrame(matrix,
                      columns=[f'File {i+1}' for i in range(file_count)],
                      index=[f'File {i+1}' for i in range(file_count)])

    plt.figure(figsize=(8, 6))
    sns.heatmap(df, annot=True, cmap="Blues", fmt=".2f")
    plt.title("File Similarity Heatmap")

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    encoded_img = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    return encoded_img


def plot_similarity_graphs(similarity_list):
    """Displays similarity scatter, line, and bar charts using Plotly."""
    df = pd.DataFrame(similarity_list)

    fig1 = px.scatter(df, x='File 1', y='File 2', color='Similarity', title='Similarity Scatter Plot')
    fig1.show()

    fig2 = px.line(df, x='File 1', y='Similarity', color='File 2', title='Similarity Line Chart')
    fig2.show()

    fig3 = px.bar(df, x='File 1', y='Similarity', color='File 2', title='Similarity Bar Chart')
    fig3.show()
