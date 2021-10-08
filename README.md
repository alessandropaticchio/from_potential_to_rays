# From Potential To Rays

This research project was carried out with a team composed by me, a colleague of mine and a researcher at [Institute for Applied Computational Science at Harvard University](https://iacs.seas.harvard.edu/).

Before diving into the explanation of the project, let me first introduce what is a **caustic**.
Citing Wikipedia:

> In optics, a caustic or caustic network is the envelope of light rays reflected or refracted by a curved surface or object, or the projection of that envelope of rays on another surface. The caustic is a curve or surface to which each of the light rays is tangent, defining a boundary of an envelope of rays as a curve of concentrated light.

A typical example of caustic is generated by the surface of the water when it's hit by light rays:

<p align="center">
<img src="/images/caustic_example.jpeg" alt="Caustic example" width="400"/>
</p>

In optics, a well-known and quite challenging problem is discovering where a caustic will appear, given the position where the rays hit a surface and the intensity of the rays themselves.

We wanted to explore whether we could leverage Deep Learning to capture this by using a dataset composed by two kinds of images:

* Potential images: they describe the points where a ray with strength *D* hits an unspecified surface.

<p align="center">
<img src="/images/ptnl_001.jpg" alt="Potential img example" width="200"/></center>
</p>

* Rays images: they describe where the caustics will emerge.

<p align="center">
<img src="/images/rays_001.jpg" alt="Potential img example" width="200"/>
</p>

In our dataset we had 7 levels of strength, namely 0.01, 0.03, 0.05, 0.07, 0.10, 0.20, 0.30, and for each strength we had 1000 couples of images, where each couple was composed by a potential image and a ray one.

Our idea was to build an architecture which could take as input a potential image and reconstruct a rays (or caustic) one.
Our architecture was composed by three sub-networks, whose component are then re-assembled:

1. A Convolutional Variational Autoencoder to reconstruct potential images 
2. A Convolutional Variational Autoencoder to reconstruct rays images 
3. A Fully Connected Neural Network to map the latent space generated from (1) to the latent space generated from (2)

After that, we would reassemble the three network in the following way, obtaining network (4):

<p align="center">
<img src="/images/architecture.png" alt="Architecture" width="800"/>
</p>

Note that networks (1) and (2) are trained by using a Mixture of Gaussian Prior, where the mean of each Gaussian is centered on the different strengths of our dataset, i.e. we had 7 different Gaussians.
This was necessary in order to encourage clustering in the latent space and facilitate the learning process of network (3).
Here we display the latent spaces obtained from training network (1) and (2)

<p align="center">
<img src="/images/rays_ls.jpg" alt="Rays latent space" width="500"/>
<img src="/images/potential_ls.png" alt="Potential latent space" width="500"/>
</p>

Some clustering is evident, in both the two latent spaces, where images with a similar strength tend to stay close, while images with dissimilar strength tend  to stay apart.
In particular, the most well-defined clusters are the ones obtained for high-strengths images.
Indeed, this is the result obtained when the network (4) is assembled:

From left to right we see:

1. The original potential image, input of the assembled net
2. The output that the net supposed to reconstruct
3. The result obtained when the input is fed into net (4)
4. The result obtained when the rays image is reconstructed through network (2)

<p align="center">
<img src="/images/high_strength_recon.jpg" alt="High strength" width="1000"/>
</p>

Ideally, we would want to have images (2), (3) and (4) as close as possible. However, given the complexity of the rays image, we do not want to reconstruct it all, but rather we only aim to grasp where the caustics emerge.
Indeed, by looking at images (3) and (4), it looks the network has a vague idea of where there might be the emergence of a caustic.

Unfortunately, when we go to lower strengths, we obtain a worse result:

<p align="center">
<img src="/images/low_strength_recon.jpg" alt="Low strength" width="1000"/>
</p>

In this case, it doesn't look like the network has enough knowledge to tell where the caustic will emerge. This is due to the not-so-perfect clustering we obtain in both the latent spaces for low strengths.
This causes the mapper between the two latent spaces not to clearly capture how to translate an image from one domain to another.
Note that, in this case, picture (4) and (2) are somehow similar, while picture (3) is quite far from the other twos.

To conclude, despite we did not manage to develop a network capable to infer where a caustic will arise under every condition, working on this project was an amazing opportunity to deepen my understanding of Deep Learning and
Computer Vision architectures, as well as learning a bit of Variational Inference.
