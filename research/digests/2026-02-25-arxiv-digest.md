# Cohera Research Digest — 2026-02-25 16:04 (Lima)

Source snapshot: `research/sources/arxiv/2026-02-25_160432.json`

## New discoveries

### 1. Region of Interest Segmentation and Morphological Analysis for Membranes in Cryo-Electron Tomography
- Topic: chaos control biological systems
- Published: 2026-02-24
- URL: http://arxiv.org/abs/2602.21195v1
- PDF: n/a
- Summary: Cryo-electron tomography (cryo-ET) enables high resolution, three-dimensional reconstruction of biological structures, including membranes and membrane proteins. Identification of regions of interest (ROIs) is central to scientific imaging, as it enables isolation and quantitative analysis of specific structural features within complex datasets. In practice, however, ROIs are typically derived indirectly through full structure segmentation followed by post hoc analysis. This limitation is especially apparent for continuous and geometrically complex structures such as membranes, which are segmented as single entities. Here, we developed TomoROIS-SurfORA, a two step framework for direct, shape-agnostic ROI segmentation and morphological surface analysis. TomoROIS performs deep learning-based ROI segmentation and can be trained from scratch using small annotated datasets, enabling practical application across diverse imaging data. SurfORA processes segmented structures as point clouds and surface meshes to extract quantitative morphological features, including inter-membrane distances, curvature, and surface roughness. It supports both closed and open surfaces, with specific considerations for open surfaces, which are common in cryo-ET due to the missing wedge effect. We demonstrate both tools using in vitro reconstituted membrane systems containing deformable vesicles with complex geometries, enabling automatic quantitative analysis of membrane contact sites and remodeling events such as invagination. While demonstrated here on cryo-ET membrane data, the combined approach is applicable to ROI detection and surface analysis in broader scientific imaging contexts.
- Citation: Xingyi Cheng, Julien Maufront, Aurélie Di Cicco, Daniël M. Pelt et al. (2026-02-24). Region of Interest Segmentation and Morphological Analysis for Membranes in Cryo-Electron Tomography. arXiv. http://arxiv.org/abs/2602.21195v1

### 2. Exact quantum transport in non-Markovian open Gaussian systems
- Topic: chaos control biological systems
- Published: 2026-02-24
- URL: http://arxiv.org/abs/2602.21190v1
- PDF: n/a
- Summary: We build an exact framework to evaluate heat, energy, and particle transport between Gaussian reservoirs mediated by a quadratic quantum system. By combining full counting statistics with newly developed non-Markovian master equation approaches, we introduce an effective master equation whose solution can be used to generate arbitrary moments of the heat statistics for any number of reservoirs. This theory applies equally to fermionic and bosonic systems, holds at arbitrarily strong coupling, and resolves out-of-equilibrium transient dynamics determined by the system's initial state. In the steady-state, weak-coupling limit, we recover results analogous to those of the well-known Landauer-Büttiker formalism. We conclude our discussion by demonstrating an application of the method to a prototypical fermionic system. Our results uncover a regime of transient negative heat conductance contingent upon the initial system preparation, providing a clear signature of non-trivial out-of-equilibrium dynamics.
- Citation: Guglielmo Pellitteri, Vittorio Giovannetti, Vasco Cavina (2026-02-24). Exact quantum transport in non-Markovian open Gaussian systems. arXiv. http://arxiv.org/abs/2602.21190v1

### 3. Human Video Generation from a Single Image with 3D Pose and View Control
- Topic: chaos control biological systems
- Published: 2026-02-24
- URL: http://arxiv.org/abs/2602.21188v1
- PDF: n/a
- Summary: Recent diffusion methods have made significant progress in generating videos from single images due to their powerful visual generation capabilities. However, challenges persist in image-to-video synthesis, particularly in human video generation, where inferring view-consistent, motion-dependent clothing wrinkles from a single image remains a formidable problem. In this paper, we present Human Video Generation in 4D (HVG), a latent video diffusion model capable of generating high-quality, multi-view, spatiotemporally coherent human videos from a single image with 3D pose and view control. HVG achieves this through three key designs: (i) Articulated Pose Modulation, which captures the anatomical relationships of 3D joints via a novel dual-dimensional bone map and resolves self-occlusions across views by introducing 3D information; (ii) View and Temporal Alignment, which ensures multi-view consistency and alignment between a reference image and pose sequences for frame-to-frame stability; and (iii) Progressive Spatio-Temporal Sampling with temporal alignment to maintain smooth transitions in long multi-view animations. Extensive experiments on image-to-video tasks demonstrate that HVG outperforms existing methods in generating high-quality 4D human videos from diverse human images and pose inputs.
- Citation: Tiantian Wang, Chun-Han Yao, Tao Hu, Mallikarjun Byrasandra Ramalinga Reddy et al. (2026-02-24). Human Video Generation from a Single Image with 3D Pose and View Control. arXiv. http://arxiv.org/abs/2602.21188v1

### 4. 823-OLT @ BUET DL Sprint 4.0: Context-Aware Windowing for ASR and Fine-Tuned Speaker Diarization in Bengali Long Form Audio
- Topic: chaos control biological systems
- Published: 2026-02-24
- URL: http://arxiv.org/abs/2602.21183v1
- PDF: n/a
- Summary: Bengali, despite being one of the most widely spoken languages globally, remains underrepresented in long form speech technology, particularly in systems addressing transcription and speaker attribution. We present frameworks for long form Bengali speech intelligence that address automatic speech recognition using a Whisper Medium based model and speaker diarization using a finetuned segmentation model. The ASR pipeline incorporates vocal separation, voice activity detection, and a gap aware windowing strategy to construct context preserving segments for stable decoding. For diarization, a pretrained speaker segmentation model is finetuned on the official competition dataset (provided as part of the DL Sprint 4.0 competition organized under BUET CSE Fest), to better capture Bengali conversational patterns. The resulting systems deliver both efficient transcription of long form audio and speaker aware transcription to provide scalable speech technology solutions for low resource languages.
- Citation: Ratnajit Dhar, Arpita Mallik (2026-02-24). 823-OLT @ BUET DL Sprint 4.0: Context-Aware Windowing for ASR and Fine-Tuned Speaker Diarization in Bengali Long Form Audio. arXiv. http://arxiv.org/abs/2602.21183v1

### 5. Circumventing the CAP Theorem with Open Atomic Ethernet
- Topic: chaos control biological systems
- Published: 2026-02-24
- URL: http://arxiv.org/abs/2602.21182v1
- PDF: n/a
- Summary: The CAP theorem is routinely treated as a systems law: under network partition, a replicated service must sacrifice either consistency or availability. The theorem is correct within its standard asynchronous network model, but operational practice depends on where partition-like phenomena become observable and on how lower layers discard or preserve semantic information about message fate. This paper argues that Open Atomic Ethernet (OAE) shifts the engineering regime in which CAP tradeoffs become application-visible by (i) replacing fire-and-forget link semantics with bounded-time bilateral reconciliation of endpoint state -- the property we call bisynchrony -- and (ii) avoiding Clos funnel points via an octavalent mesh in which each node can act as the root of a locally repaired spanning tree. The result is not the elimination of hard graph cuts, but a drastic reduction in the frequency and duration of application-visible "soft partitions" by detecting and healing dominant fabric faults within hundreds of nanoseconds. We connect this view to Brewer's original CAP framing, the formalization by Gilbert and Lynch, the CAL theorem of Lee et al., which replaces binary partition tolerance with a quantitative measure of apparent latency, and Abadi's PACELC extension.
- Citation: Paul Borrill (2026-02-24). Circumventing the CAP Theorem with Open Atomic Ethernet. arXiv. http://arxiv.org/abs/2602.21182v1

### 6. Memory Undone: Between Knowing and Not Knowing in Data Systems
- Topic: metabolic health systems biology
- Published: 2026-02-24
- URL: http://arxiv.org/abs/2602.21180v1
- PDF: n/a
- Summary: Machine learning and data systems increasingly function as infrastructures of memory: they ingest, store, and operationalize traces of personal, political, and cultural life. Yet contemporary governance demands credible forms of forgetting, from GDPR-backed deletion to harm-mitigation and the removal of manipulative content, while technical infrastructures are optimized to retain, replicate, and reuse. This work argues that "forgetting" in computational systems cannot be reduced to a single operation (e.g., record deletion) and should instead be treated as a sociotechnical practice with distinct mechanisms and consequences. We clarify a vocabulary that separates erasure (removing or disabling access to data artifacts), unlearning (interventions that bound or remove a data point influence on learned parameters and outputs), exclusion (upstream non-collection and omission), and forgetting as an umbrella term spanning agency, temporality, reversibility, and scale. Building on examples from machine unlearning, semantic dependencies in data management, participatory data modeling, and manipulation at scale, we show how forgetting can simultaneously protect rights and enable silencing. We propose reframing unlearning as a first-class capability in knowledge infrastructures, evaluated not only by compliance or utility retention, but by its governance properties: transparency, accountability, and epistemic justice.
- Citation: Viktoriia Makovska, George Fletcher, Julia Stoyanovich, Tetiana Zakharchenko (2026-02-24). Memory Undone: Between Knowing and Not Knowing in Data Systems. arXiv. http://arxiv.org/abs/2602.21180v1

### 7. XMorph: Explainable Brain Tumor Analysis Via LLM-Assisted Hybrid Deep Intelligence
- Topic: metabolic health systems biology
- Published: 2026-02-24
- URL: http://arxiv.org/abs/2602.21178v1
- PDF: n/a
- Summary: Deep learning has significantly advanced automated brain tumor diagnosis, yet clinical adoption remains limited by interpretability and computational constraints. Conventional models often act as opaque ''black boxes'' and fail to quantify the complex, irregular tumor boundaries that characterize malignant growth. To address these challenges, we present XMorph, an explainable and computationally efficient framework for fine-grained classification of three prominent brain tumor types: glioma, meningioma, and pituitary tumors. We propose an Information-Weighted Boundary Normalization (IWBN) mechanism that emphasizes diagnostically relevant boundary regions alongside nonlinear chaotic and clinically validated features, enabling a richer morphological representation of tumor growth. A dual-channel explainable AI module combines GradCAM++ visual cues with LLM-generated textual rationales, translating model reasoning into clinically interpretable insights. The proposed framework achieves a classification accuracy of 96.0%, demonstrating that explainability and high performance can co-exist in AI-based medical imaging systems. The source code and materials for XMorph are all publicly available at: https://github.com/ALSER-Lab/XMorph.
- Citation: Sepehr Salem Ghahfarokhi, M. Moein Esfahani, Raj Sunderraman, Vince Calhoun et al. (2026-02-24). XMorph: Explainable Brain Tumor Analysis Via LLM-Assisted Hybrid Deep Intelligence. arXiv. http://arxiv.org/abs/2602.21178v1

### 8. Bayesian Parametric Portfolio Policies
- Topic: digital twins uncertainty
- Published: 2026-02-24
- URL: http://arxiv.org/abs/2602.21173v1
- PDF: n/a
- Summary: Parametric Portfolio Policies (PPP) estimate optimal portfolio weights directly as functions of observable signals by maximizing expected utility, bypassing the need to model asset returns and covariances. However, PPP ignores policy risk. We show that this is consequential, leading to an overstatement of expected utility and an understatement of portfolio risk. We develop Bayesian Parametric Portfolio Policies (BPPP), which place a prior on policy coefficients thereby correcting the decision rule. We derive a general result showing that the utility gap between PPP and BPPP is strictly positive and proportional to posterior parameter uncertainty and signal magnitude. Under a mean--variance approximation, this correction appears as an additional estimation-risk term in portfolio variance, implying that PPP overexposes when signals are strongest and when risk aversion is high. Empirically, in a high-dimensional setting with 242 signals and six factors over 1973--2023, BPPP delivers higher Sharpe ratios, substantially lower turnover, larger investor welfare, and lower tail risk, with advantages that increase monotonically in risk aversion and are strongest during crisis episodes.
- Citation: Miguel C. Herculano (2026-02-24). Bayesian Parametric Portfolio Policies. arXiv. http://arxiv.org/abs/2602.21173v1
