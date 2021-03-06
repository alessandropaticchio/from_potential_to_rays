from models import ConvVAE, ConvVAETest, Mapper
from constants import *
from utils import StrengthDataset, generate_dataset_from_strength
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import torch
import random

batch_size = 1
strengths = [0.01, 0.03, 0.05]
dataset = 'potential'
model_name = 'potential_VAE_[0.01, 0.03, 0.05]_2021-08-03 12_56_09.373712.pt'
mapper_model_name = 'Mapper_2021-05-02 06_23_12.374117.pt'
net_size = 1
conditional = False
mapping = False

model_path = MODELS_ROOT + model_name
mapper_model_path = MODELS_ROOT + mapper_model_name

if dataset == 'potential':
    pics_train_dataset = torch.load(DATA_ROOT + 'RP_images/loaded_data/' + 'training_' + dataset + '.pt')
else:
    pics_train_dataset = torch.load(DATA_ROOT + 'RP_images/loaded_data/' + 'training_' + dataset + '.pt')

strength_train_dataset = torch.load(DATA_ROOT + 'RP_images/loaded_data/' + 'training_strength.pt')
pics_train_dataset, strength_train_dataset = generate_dataset_from_strength(pics_train_dataset, strength_train_dataset,
                                                                            strengths)

train_dataset = StrengthDataset(x=pics_train_dataset, d=strength_train_dataset)

train_loader = torch.utils.data.DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)

if dataset == 'rays':
    image_size = RAYS_IMAGE_SIZE
    image_channels = RAYS_IMAGE_CHANNELS
    hidden_size = RAYS_HIDDEN_SIZE
    # hidden_size = 8 * 47 * 47
    latent_size = RAYS_LATENT_SIZE
    image_channels = RAYS_IMAGE_CHANNELS
else:
    image_size = POTENTIAL_IMAGE_SIZE
    image_channels = POTENTIAL_IMAGE_CHANNELS
    hidden_size = POTENTIAL_HIDDEN_SIZE
    # hidden_size = 8 * 47 * 47
    latent_size = POTENTIAL_LATENT_SIZE
    image_channels = POTENTIAL_IMAGE_CHANNELS

h0 = POTENTIAL_LATENT_SIZE * 2
h1 = RAYS_LATENT_SIZE * 2
h2 = RAYS_LATENT_SIZE * 2
h3 = RAYS_LATENT_SIZE * 2

vae = ConvVAE(image_dim=image_size, hidden_size=hidden_size, latent_size=latent_size, image_channels=image_channels,
              net_size=net_size, conditional=conditional)

vae.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
vae.eval()

if mapping:
    mapper = Mapper(h_sizes=[h0, h1, h2, h3])
    mapper.load_state_dict(torch.load(mapper_model_path, map_location=torch.device('cpu')))
    mapper.eval()

encodings = []
encoded_strengths = []

max_samples = 1000

for i in range(max_samples):
    idx = random.randint(0, len(train_dataset) - 1)
    pic_sample = train_dataset[idx][0].unsqueeze(0).float()
    strength_sample = train_dataset[idx][1].unsqueeze(0)
    mean, log_var = vae.encode(pic_sample, strength_sample)
    sample_encoded = torch.cat((mean, log_var), 0).flatten()

    if mapping:
        sample_encoded = mapper(sample_encoded)

    sample_encoded = sample_encoded.tolist()

    encodings.append(sample_encoded)
    encoded_strengths.append(train_dataset[idx][1])

encodings_embedded = TSNE(n_components=2).fit_transform(encodings)

# from sklearn.decomposition import PCA
# encodings_embedded = PCA(n_components=1).fit_transform(encodings)

colors = [STRENGTHS_COLORS[round(strength.item(), 2)] for strength in encoded_strengths]

fig, ax = plt.subplots()
scatter = ax.scatter(encodings_embedded[:, 0], encodings_embedded[:, 1], c=encoded_strengths, cmap='plasma')
legend = ax.legend(*scatter.legend_elements(), loc="best", title="Strengths")
ax.add_artist(legend)
plt.title('T-SNE visualization of {} encodings'.format(dataset))
plt.show()
