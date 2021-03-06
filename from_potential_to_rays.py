from models import ConvVAE, ConvVAETest, Mapper
from utils import StrengthDataset, generate_dataset_from_strength
from constants import *
import random
import matplotlib.pyplot as plt
from torchvision import transforms
import matplotlib.patches as mpatches

potential_model_name = 'potential_VAE_[0.01, 0.03, 0.05, 0.07, 0.1, 0.2, 0.3]_2021-06-24 15_34_11.213966.pt'
rays_model_name = 'rays_VAE_[0.01, 0.03, 0.05, 0.07, 0.1, 0.2, 0.3]_2021-06-27 08_22_54.069847.pt'
mapper_model_name = 'Mapper_2021-06-27 10_24_06.336316.pt'
potential_model_path = MODELS_ROOT + potential_model_name
rays_model_path = MODELS_ROOT + rays_model_name
mapper_model_path = MODELS_ROOT + mapper_model_name
strengths = [0.07]
train = True
net_size = 1
n_forwards = 10

power = 1

potential_train_dataset_full = torch.load(DATA_ROOT + 'RP_images/loaded_data/' + 'training_potential.pt')
potential_test_dataset_full = torch.load(DATA_ROOT + 'RP_images/loaded_data/' + 'test_potential.pt')

rays_train_dataset_full = torch.load(DATA_ROOT + 'RP_images/loaded_data/' + 'training_rays.pt')
rays_test_dataset_full = torch.load(DATA_ROOT + 'RP_images/loaded_data/' + 'test_rays.pt')

strength_train_dataset_full = torch.load(DATA_ROOT + 'RP_images/loaded_data/' + 'training_strength.pt')
strength_test_dataset_full = torch.load(DATA_ROOT + 'RP_images/loaded_data/' + 'test_strength.pt')

potential_train_dataset, strength_train_dataset = generate_dataset_from_strength(potential_train_dataset_full,
                                                                                 strength_train_dataset_full,
                                                                                 strengths)
potential_test_dataset, strength_test_dataset = generate_dataset_from_strength(potential_test_dataset_full,
                                                                               strength_test_dataset_full,
                                                                               strengths)

rays_train_dataset, _ = generate_dataset_from_strength(rays_train_dataset_full, strength_train_dataset_full,
                                                       strengths)
rays_test_dataset, _ = generate_dataset_from_strength(rays_test_dataset_full, strength_test_dataset_full,
                                                      strengths)

potential_vae = ConvVAE(image_dim=POTENTIAL_IMAGE_SIZE, hidden_size=POTENTIAL_HIDDEN_SIZE,
                        latent_size=POTENTIAL_LATENT_SIZE,
                        image_channels=POTENTIAL_IMAGE_CHANNELS,
                        net_size=net_size)
potential_vae.load_state_dict(torch.load(potential_model_path, map_location=torch.device('cpu')))
potential_vae.eval()

rays_vae = ConvVAE(image_dim=RAYS_IMAGE_SIZE, hidden_size=RAYS_HIDDEN_SIZE, latent_size=RAYS_LATENT_SIZE,
                   image_channels=RAYS_IMAGE_CHANNELS,
                   net_size=net_size)
rays_vae.load_state_dict(torch.load(rays_model_path, map_location=torch.device('cpu')))
rays_vae.eval()

h_sies = H_SIZES

mapper = Mapper(h_sizes=h_sies)
mapper.load_state_dict(torch.load(mapper_model_path, map_location=torch.device('cpu')))
mapper.eval()

if train:
    potential_dataset = potential_train_dataset
    rays_dataset = rays_train_dataset
    strength_dataset = strength_train_dataset
else:
    potential_dataset = potential_test_dataset
    rays_dataset = rays_test_dataset
    strength_dataset = strength_test_dataset

rand_sample_idx = random.randint(1, len(potential_dataset))
predicted_samples = []

for i in range(1, n_forwards):
    # Encoding

    pic_potential_sample = potential_dataset.data[rand_sample_idx].unsqueeze(0)
    strength_potential_sample = strength_dataset.data[rand_sample_idx].unsqueeze(0)
    potential_mean, potential_log_var = potential_vae.encode(pic_potential_sample, strength_potential_sample)
    potential_sample_encoded = torch.cat((potential_mean, potential_log_var), 1)

    # Mapping
    mapping = mapper(potential_sample_encoded)

    rays_mean = mapping[:, :RAYS_LATENT_SIZE]
    rays_log_var = mapping[:, RAYS_LATENT_SIZE:]
    # rays_mean = potential_mean
    # rays_log_var = potential_log_var

    rays_sample_mapped = rays_vae.decode(rays_mean, rays_log_var, strength_potential_sample)
    rays_sample_mapped = torch.pow(rays_sample_mapped, power)

    # Reconstructing the original image for comparison
    rays_sample_reconstructed = rays_vae(rays_dataset.data[rand_sample_idx].unsqueeze(0), strength_potential_sample)[0]

    predicted_samples.append(rays_sample_reconstructed)

rays_sample_reconstructed = torch.mean(torch.stack(predicted_samples), dim=0)
rays_sample_reconstructed = torch.pow(rays_sample_reconstructed, power)

plt.figure(figsize=(10, 5))
plt.subplot(1, 4, 1)
plt.title('Original Potential \n strength = {:.2f} \n dataset idx = {}'.format(strength_potential_sample.item(),
                                                                               rand_sample_idx))
plt.imshow(pic_potential_sample.squeeze(0).permute(1, 2, 0).detach().numpy())

plt.subplot(1, 4, 2)
plt.title('Original Rays')
plt.imshow(rays_dataset[rand_sample_idx].permute(1, 2, 0).detach().numpy())

plt.subplot(1, 4, 3)
plt.title('Mapped Rays')
plt.imshow(rays_sample_mapped.squeeze(0).permute(1, 2, 0).detach().numpy())

plt.subplot(1, 4, 4)
plt.title('VAE-Reconstructed Rays')
plt.imshow(rays_sample_reconstructed.squeeze(0).permute(1, 2, 0).detach().numpy())

# scintillation index
plt.figure()


rays_sample_mapped = transforms.Compose([
    transforms.Grayscale(num_output_channels=1)
])(rays_sample_mapped.squeeze(0))

rand_sample = rays_dataset[rand_sample_idx]

rand_sample = transforms.Compose([
    transforms.Grayscale(num_output_channels=1)
])(rand_sample.squeeze(0))

I_mean = torch.mean(rays_sample_mapped, dim=1)
I_var = torch.var(rays_sample_mapped, dim=1)

I_mean_real = torch.mean(rand_sample, dim=1)
I_var_real = torch.var(rand_sample, dim=1)

s = (I_var / I_mean) - 1
s_real = (I_var_real / I_mean_real) - 1

plt.title('Scintillation Index')
plt.plot(s.squeeze().detach().numpy(), label="reconstructed")
plt.plot(s_real.squeeze().detach().numpy(), label='original')

blue_patch = mpatches.Patch(color='blue', label='Reconstructed')
orange_patch = mpatches.Patch(color='orange', label='Original')
plt.legend(handles=[blue_patch, orange_patch])

plt.show()
