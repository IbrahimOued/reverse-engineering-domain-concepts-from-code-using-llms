from sentence_transformers import (SentenceTransformer, util)
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans        
from sklearn.manifold import TSNE
from matplotlib import pyplot as plt
from config import project as config

class CustomEmbedder:
    def __init__(self, model=config['models']['embedder']):
        self.embedding_model = SentenceTransformer(model)
        self.model_directory = "/tmp/sbert_model"
        self.embedding_model.save(self.model_directory)
        self.artifacts = {"model_path": self.model_directory}

    def embed(self, text):
        embeddings = self.embedding_model.encode(text, convert_to_tensor=True, show_progress_bar=False)
        return embeddings.cpu().numpy()
        


    def calculate_similarity(self, class_1_context, class_2_context):        
        class_1_emb = self.embedding_model.encode(class_1_context, convert_to_tensor=True)
        class_2_emb = self.embedding_model.encode(class_2_context, convert_to_tensor=True)
        cosine_scores = util.cos_sim(class_1_emb, class_2_emb)
        return cosine_scores.cpu().numpy()[0][0]


    def kmean_clustering(self, names, embeddings, n_clusters=4):
        # Perform k-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(embeddings)

        # Use TSNE for dimensionality reduction
        tsne = TSNE(n_components=2, random_state=42)
        embeddings_tsne = tsne.fit_transform(embeddings)

        # Create a DataFrame for easy plotting
        df = pd.DataFrame(embeddings_tsne, columns=['Dimension 1', 'Dimension 2'])
        df['Word'] = names
        df['Cluster'] = clusters.astype(str)

        # Plot the clustered word embeddings using seaborn
        plt.figure(figsize=(10, 8))
        sns.scatterplot(x='Dimension 1', y='Dimension 2', data=df, hue='Cluster', palette='viridis', s=100)

        # Annotate each point with its corresponding word
        for i, row in df.iterrows():
            plt.annotate(row['Word'], (row['Dimension 1'], row['Dimension 2']), fontsize=8)

        plt.title('Word Embeddings Clustering Visualization')
        plt.show()


    def plot_tsne(self, names, embeddings, dimensions=2, title="Word Embeddings Scatter Plot"):
        # Load SentenceTransformer model

        # Use TSNE for dimensionality reduction
        tsne = TSNE(n_components=dimensions, random_state=42)
        embeddings_tsne = tsne.fit_transform(embeddings)

        # Create a DataFrame for easy plotting
        df = pd.DataFrame(embeddings_tsne, columns=['Dimension 1', 'Dimension 2'])
        df['Class names'] = names

        # Plot the word embeddings using seaborn
        plt.figure(figsize=(10, 8))
        sns.scatterplot(x='Dimension 1', y='Dimension 2', data=df, hue='Class names', palette='viridis', s=100)

        # Annotate each point with its corresponding word
        for i, word in enumerate(names):
            plt.annotate(word, (embeddings_tsne[i, 0], embeddings_tsne[i, 1]), fontsize=8)

        plt.xlabel("Dimension 1")
        plt.ylabel("Dimension 2")
        plt.title(title)
        plt.legend(loc="upper left", title="Words")
        plt.show()