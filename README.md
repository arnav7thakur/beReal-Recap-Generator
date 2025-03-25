# beReal
This [file ](https://github.com/arnav7thakur/beReal-Recap-Generator/blob/main/BeReal-Recap-Generator-Generalized%20.ipynb) consists of the working code. The other files include the experimentation. 
 
The "BeReal Recap Enhancement Project" was initiated following dissatisfaction with the 2023 recap feature of the social media application BeReal. This project aimed to improve the user experience by creating a more immersive and personalized recap video.

The journey began with obtaining images from BeReal using a third-party website, 'toofake.lol,' to overcome limitations in the platform's provided recap. A suitable song was then selected to accompany the images, enhancing the overall experience.

Using a Jupyter notebook, the synchronization process commenced. Various Python libraries including librosa, numpy, pydub, moviepy, and PIL were employed for audio analysis, image manipulation, and video creation.

Challenges arose initially with timing synchronization, prompting the exploration of alternative approaches. Calculating frames per beat and setting a threshold for peak identification in the audio waveform were among the strategies employed.

After iterative experimentation and refinement, a novel approach based on amplitude thresholding and segment-based peak analysis was devised. This method optimized the synchronization process by distributing images based on peak counts within music segments.

The meticulous approach resulted in the seamless synchronization of over 300 images with the upbeat audio, culminating in a cohesive and engaging recap video for enhanced user enjoyment.
