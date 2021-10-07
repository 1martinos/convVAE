import numpy as np
import torch 
import torch.nn as nn
import h5py as h
import torch.nn.functional as F

class cVAE(nn.Module):
    def __init__(self,input_shape,
                      latent_dim,
                      hidden_dim=None,
                      n_channels=100,
                      kernel=5,
                      fc_out=64):
        super().__init__()
        # Encoder Layers
        self.z_dim = latent_dim
        self.input_shape = input_shape
        self.n_channels = n_channels
        self.fc_out = fc_out

        # Also swapped all to ReLU
        self.encoder = nn.Sequential(
            nn.Conv2d(1,n_channels,kernel,stride=1,padding=1),
            nn.ReLU(0.2),

            nn.Conv2d(n_channels,n_channels,kernel,stride=1,padding=1),
            nn.ReLU(0.2),

            nn.Conv2d(n_channels,n_channels,kernel,stride=2,padding=1),
            nn.ReLU(0.2),

            nn.Conv2d(n_channels,1,kernel,stride=1,padding=1),
            nn.ReLU(0.2),
        )
        print(f"ENCODER SHAPE: {self.encoder(test_data).shape}")
        self.flat_layer = nn.Flatten()

        test_data = torch.rand((1,1,*input_shape))
        if hidden_dim is None:
            self.final_size = self.encoder(test_data).shape[1:]
            self.hidden = self.flat_layer(
                                self.encoder(test_data)
                                    ).shape[-1]
        self.fcEnc = nn.Linear(self.hidden, 64)
        self.enc_actv = nn.ReLU()
        self.mean = nn.Linear(self.fc_out,self.z_dim)
        self.logvar = nn.Linear(self.fc_out,self.z_dim)

        # Decoder Layers
        self.fcDec = nn.Linear(self.z_dim,self.hidden)
        self.dec_actv = nn.ReLU()
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(1,n_channels,kernel,stride=1,padding=1),
            nn.ReLU(),

            nn.ConvTranspose2d(n_channels,n_channels,kernel,stride=2,padding=1,
                               output_padding=1),
            nn.ReLU(),

            nn.ConvTranspose2d(n_channels,n_channels,kernel,stride=1,padding=1),
            nn.ReLU(),

            nn.ConvTranspose2d(n_channels,1,kernel,stride=1,padding=1),
            #nn.Sigmoid(), # No sigmoid because using logits
        )
        print(f"DECODER SHAPE: {self.decoder(self.encoder(test_data)).shape}")

    def sample(self, log_var, mean):
        std = torch.exp(0.5 * log_var)
        eps = torch.randn_like(std)
        return eps.mul(std).add_(mean)

    def encode(self,x):
        x = self.encoder(x)
        x = self.flat_layer(x)

        # added in extra linear layer before mean and logvar
        x = self.fcEnc(x)
        x = self.enc_actv(x)

        mu = self.mean(x) 
        lv = self.logvar(x)
        z = self.sample(mu,lv)
        return z,mu,lv

    def decode(self,z):
        z = self.fcDec(z)
        x = self.dec_actv(x)
        z = z.view(-1,*self.final_size)
        output = self.decoder(z)
        return output

    def forward(self,x):
        z,mu,lv = self.encode(x)
        recon = self.decode(z)
        recon = recon.reshape(-1,*self.input_shape)
        return recon,mu,lv,z

    def embed(cmap):
        return encode(cmap)[0]
