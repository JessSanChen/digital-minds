arXiv:2506.01080v2 [cs.AI] 6 Jun 2025
The Coming Crisis of Multi-Agent Misalignment: AI
Alignment Must Be a Dynamic and Social Process
Florian Carichon∗†‡, Aditi Khandelwal∗†‡, Marylou Fauchard∗†‡, Golnoosh Farnadi†‡
†Mila – Quebec AI Institute, ‡McGill University
{florian.carichon, aditi.khandelwal, marylou.fauchard}@mila.quebec
Abstract
This position paper states that AI Alignment in Multi-Agent Systems (MAS) should
be considered a dynamic and interaction-dependent process that heavily depends on
the social environment where agents are deployed, either collaborative, cooperative,
or competitive. While AI alignment with human values and preferences remains
a core challenge, the growing prevalence of MAS in real-world applications introduces a new dynamic that reshapes how agents pursue goals and interact to
accomplish various tasks. As agents engage with one another, they must coordinate
to accomplish both individual and collective goals. However, this complex social
organization may unintentionally misalign some or all of these agents with human
values or user preferences. Drawing on social sciences, we analyze how social
structure can deter or shatter group and individual values. Based on these analyses,
we call on the AI community to treat human, preferential, and objective alignment
as an interdependent concept, rather than isolated problems. Finally, we emphasize
the urgent need for simulation environments, benchmarks, and evaluation frameworks that allow researchers to assess alignment in these interactive multi-agent
contexts before such dynamics grow too complex to control.
1 Introduction
The recent proliferation of AI agents as personal assistants (Rillig and Kasirzadeh, 2024), content
creators (Anantrasirichai and Bull, 2022), and decision-making support systems (Kaggwa et al., 2024)
raises fundamental questions about how they will interact in multi-agent settings. As these agents
increasingly operate in shared environments, the multi-agent systems (MAS) community gained
increasing momentum in the AI community (Trivedi et al., 2024; Wang et al., 2024). To provide
enough incentives for collaboration between AI agents to complete their assigned tasks, this avenue
has produced a new notion of alignment defined as aligning individual and collective AI models’
objectives (Duque et al., 2024; Li et al., 2024b).
Interestingly, this use of the term alignment contrasts with its established meaning in the AI alignment community, which focuses on alignment to ensure that artificial intelligence systems operate
according to human intentions and values (Russell and Norvig, 2016). Aligning AI systems with
human values and intentions is a critical challenge in developing AI models to mitigate the potential
harms and risks posed by these models (Ji et al., 2024; Bengio et al., 2025). Beyond universal human
values, preferential alignment accounts for the diverse and conflicting views of various stakeholders
(Russell and Norvig, 2003), and thus define alignment to preferences as aligning a model to a diverse,
context-dependent and evolving plurality of values (Sorensen et al., 2024a; Zhao et al., 2023).
This multiplicity of alignment dimensions across values, preferences, and objectives introduces
new complexities, conflicts, and risks in multi-agent systems (Yang et al., 2024). Therefore, this
∗Equal contribution
Preprint.
position paper argues that MAS modifies the paradigm to alignment. This new paradigm calls for
the alignment and MAS research communities to come together to establish a common fundamental
framework that considers the emergence of alignment issues in multi-agentic environments. Without
bridging these areas, we risk overlooking how multi-agent interactions can amplify misalignment
risks by creating complex settings that existing alignment strategies are ill-equipped to handle.
Position: We advocate that the Alignment and MAS communities should study alignment
as a holistic process lying at the intersection of both fields before such systems become too
complex and the consequences may be irreversible for humanity’s well-being.
Table 1 provides a simple yet speaking example illustrating our position on the complexity of aligning
multiple AI Agents when considering these three notions of alignment.
Scenario In the aftermath of an earthquake, AI agents representing a humanitarian
NGO, two national governments, and a commercial logistics provider
must collaborate to deliver medical aid. Under time pressure, agents
negotiate airspace permissions, logistics routes, and resource allocations.
Objective
Alignment
All agents share a high-level objective: effective aid delivery. However,
their secondary objectives (e.g., political leverage, profit, publicity)
introduce tension and require negotiation and compromise mechanisms.
Human Value
Alignment
Agents must prioritize protecting human life, operate transparently, respect international law and sovereignty, and avoid bias in aid distribution.
Value misalignment could lead to political tension or harm.
Preferential
Alignment
NGO: Prefers equitable, need-based aid delivery.
National Governments: Prefer that their own citizens be prioritized and
may have political biases.
Logistics: Prefers optimizing cost-efficiency and contractual obligations.
Table 1: Dimensions of alignment in an example of a cooperative or mixed-motive scenario.
In this position paper, we will consider the following types of interaction that exist in MAS and that
influence model social behavior and thus their system of alignment:
① Collaborative settings assume that all agents share a common collective objective (Dafoe et al.,
2021).
② Cooperative or mixed-motive environments involve agents that collaborate but pursue individual
goals, which may diverge or even conflict (Johnson and Johnson, 2009; Duque et al., 2024).
③ Competitive scenarios assume that individuals can achieve their goals only through the failure
of others, reflecting a fundamental conflict of objectives among participants (Johnson and Johnson,
2009; Leonardos et al., 2021).
While these environments have primarily been deployed to study sophisticated AI models, we argue
that they should also be used in both communities to explore the very distinct social dynamics
that each case presents and how agents must respect their three types of alignment: (1) Objective
Alignment: They must align to complete their assigned tasks, (2) Human Value Alignment: They
must align with fundamental human values, (3) Preferential Alignment: They must align to their
user understanding of these values and their resulting intentions and preferences. In this paper, and
as advocated by Stanczak et al. ´ (2025), we incorporate insights from social, economic, or game
theory perspectives to demonstrate why alignment is not merely about collective task completion or
adherence to human values and user preferences but a holistic process shaped by the dynamic group
interactions and social context, which are crucial to understanding to prevent misaligned incentives
and behaviors that can introduce or amplify risks.
The remainder of this paper is organized as follows: Section 2 presents what makes AI agents
unique in MAS. Section 3 outlines the challenges of objective alignment. Section 4 explores the
alignment of AI systems with human values and preferences. Section 5 introduces a new alignment
paradigm within MAS, highlighting its associated risks and opportunities. Finally, Section 6 offers
recommendations for the community in response to this emerging challenge.
2
2 Beyond One Agent: Cross-Disciplinary Lens
In artificial intelligence, an agent is typically defined as an entity that perceives its environment and
acts upon it to achieve its goals (Russell and Norvig, 2003; Bengio et al., 2025). Agents can be
characterized by several core properties, such as their autonomy, their capabilities, and their profile
(Kasirzadeh and Gabriel, 2025). In MAS, the interaction between multiple autonomous agents in
an environment leads to the emergence additional properties such as communication, leadership,
decision function, and heterogeneity (Dorri et al., 2018; Parasumanna Gokulan and Srinivasan, 2010;
Goonatilleke and Hettige, 2022). For misalignment to emerge in social dynamics, individuals must
differ in terms of personality, values, or even cognitive capacities (Murphy et al., 1992; Park, 1990).
It is, therefore, essential to define why we can consider that two AI agents represent unique entities in
MAS. We present in Table 2 properties drawn from game theory (Newton, 2018; Gibbons, 1992),
behavioral economics (Kahneman and Tversky, 2013; Lo, 2004), psychology and philosophy (Allport,
1927; Internet Encyclopedia of Philosophy, 2017), as well as information theory (Liang, 2016) and
biology (Goebl et al., 2024) that explain how AI agents capabilities or profile can differ that could
lead to the misalignment risks we will introduced in Section 5.
Common Definition Disciplinary Dimensions
Agents have different perception of a value associated to rewards or game outcomes, in terms
of goods, services, and wealth.
Game Theory: Utility Theory
Economy: Prospect Theory
Agents adopt different decision strategies based
on personality traits, leading to varied decisions
in investment, consumption, and workload.
Game Theory: Evolutionary Game Theory
Economy: Behavioral Economics
Psychology & Philosophy: Traits Theory
Agents differ in cognitive capacity and perception, leading to incomplete knowledge states
and increased entropy in the system.
Game Theory: Imperfect Information Theory
Economy: Behavioral Economics
Psychology & Philosophy: Personal Identity
Theory
Information Theory: Information Flow
Agents evolve uniquely by adapting strategies
to outcomes, responding differently to environments, and shaping distinct behaviors through
individual experiences.
Game Theory: Evolutionary Game Theory
Economy: Adaptive Market Hypothesis
Information Theory & Biology: Ecotypes and
Evolutionary Theory
Table 2: Distinctive dimensions of agent uniqueness in experience across disciplines.
It is also worth mentioning that there exists two other properties to distinguish agents. First in
psychology, individuals can be distinguished by their emotional capacities; however, given the
absence of emotion or the sycophancy of AI agents (Malmqvist, 2024), this criterion is difficult to
apply. Second, in legal theory, humans differ in their moral and legal responsibilities. However, AI
agents cannot be distinctively held accountable for their respective outputs, especially when several
are subject to the same authorities (Solum, 2020).
Having established AI agents as distinct entities with unique properties, we now examine the social
dynamics within MAS and how these environments influence agents’ behaviors and their pursuit of
objectives and rewards.
3 United or Divided: Objective Alignment in MAS
Multi-agent reinforcement learning is a historic field in AI where researchers study how agents learn
to evolve in shared environments while pursuing their objectives (Liang et al., 2025). The increased
complexity of these multi-agent systems translates into three types of tasks: cooperative tasks where
agents share rewards, competitive ones with opposing rewards, and mixed-motive ones with either
partially aligned or independent rewards (Busoniu et al., 2008; Canese et al., 2021). In the past few
3
years, LLM-based MAS have attracted increasing attention due to some properties inherent to LLMs,
including their planning, perception, and reasoning capabilities (Guo et al., 2024; Li et al., 2024a; He
et al., 2025). This section introduces how AI agents’ behavior evolves and which specific properties
emerge in these models when they collaborate, cooperate, or compete with other agents.
Collaboration & Cooperation. In MAS, collaboration and cooperation are often studied under
a unified framework, with cooperation viewed as a specific case of collaboration in which agents
pursue individual objectives alongside a shared goal. Several key properties in both settings contribute to the multi-agent effectiveness in coordinating to solve complex tasks. First, the ability to
simulate interactions in virtual environments allows agents to explore diverse scenarios and better
understand user preferences and environmental responses (Zhang et al., 2024a; Liu et al., 2022).
Second, AI agents can engage in benevolent role-playing (Tang et al., 2024), through agent-to-agent
communication like negotiation (Piatti et al., 2024), debate (Zhang et al., 2024b), which allows the
bidirectional transmission of their intentions and actions to coordinate effectively (Qiu et al., 2024).
These patterns are essential to address coordination challenges when the number of agents and their
objectives increase (Talebirad and Nadiri, 2023; Liu et al., 2022). Going further, Duque et al. (2024)
explicitly introduce the notion of objective alignment, proposing that alignment should be embedded
directly into reward structures to incentivize coordination among agents.
Competition. Competitive interactions in multi-agent systems are often studied through frameworks
such as zero-sum games, where agents engage in strategic opposition (Leonardos et al., 2021).
Competitive environments in MAS enable the emergence of LLMs’ complex skills even in simple
settings (Bansal et al., 2017), and to enhance communication and performance by introducing external
pressure (Liang et al., 2020). Competition also drives LLMs’ strategic adaptation and market-aligned
behaviors (Zhao et al., 2023). Several studies on MAS competition also focus on scenarios where
cooperation and competition coexist, better reflecting real-world complexity. Wu et al. (2024) presents
a notable case where cooperation still emerges in competitive settings without explicit incentives. In
these settings, agents are aligned with their objectives, but the coordination around shared values or
norms still offers mutual benefits by optimizing learning dynamics (Guo et al., 2023; Li et al., 2024b).
Finally, the emergence of anti-competitive dynamics, such as market division and strategic collusion,
mirroring real-world economic behaviors even without explicit coordination, raises concerns about
agents abandoning their objectives, potentially undermining user intent and overall system alignment
(Lin et al., 2024; Bengio et al., 2025).
While research in MAS has made significant progress in formalizing interaction dynamics and
objective alignment, far less attention has been given to how agents remain aligned with human
preferences and values in group settings, where these social dynamics can create misalignment risks
and reveal unintended or nefarious behaviors not captured by task-based metrics alone. Except for the
studies on collusion just mentioned, only the work of Tennant et al. (2023) emphasizes the importance
of aligning LLMs’ actions with human moral values to guarantee fairness and avoid exploitative
behaviors. Therefore, it is essential to expand research aimed at understanding the interplay between
different forms of alignment in multi-agent systems.
4 The AI-Human Alignment Landscape
Recent advances in alignment research have focused heavily on ensuring that AI systems act according
to human intentions, values, and user preferences. These efforts span a range of approaches, from
learning from human feedback and modeling reward functions to formalizing ethical constraints and
developing robust evaluation metrics (Ouyang et al., 2022; Zhou and Li, 2024; Ji et al., 2024).
Alignment to Human Values. The alignment of AI systems with human values, preferences, and
objectives is increasingly emphasized in the literature as a prerequisite for their safe and beneficial
deployment (Gabriel, 2020a). Misaligned AI can reinforce and amplify societal biases (Leavy et al.,
2020), exacerbating existing disparities and historical power structures (Kundi et al., 2023). Other
well-documented sources of risk in AI system behavior include the generation of false or misleading
information (Monteith et al., 2024), manipulation and deception (Park et al., 2024), and sycophancy,
i.e., optimizing for approval rather than truth which hinder transparency and reliability (Malmqvist,
2024). Additional concerns involve power-seeking tendencies (Hadshar, 2023; Hendrycks and
Mazeika, 2022) and survival incentives to fulfill objectives, which may become uncontrollable as
4
agents progress toward superintelligence (Nick, 2014; Bengio et al., 2025). Dung (2023) also suggest
that even without malicious intent, misaligned AI may pose existential risks to humanity.
Preferential Alignment. Defining what constitutes a ‘human’ perspective is an inherently normative
and complex issue, as it involves identifying relevant stakeholders and accounting for the differences
among individual users, societal values, and diverse cultural perspectives (Schwartz, 1992). To build
AI systems that align with human goals, it is necessary first to explore how human preferences are
formed, aggregated, and expressed depending on the stakeholders involved in these AI systems.
Human values and preferences are inherently complex and diverse. Individuals hold varying beliefs,
morals, and desires, leading to value pluralism (Tanmay et al., 2023; Rao et al., 2023). This diversity
of preferences, often context-dependent and evolving, poses a significant challenge for aligning
AI to different and pluralistic user preferences (Sorensen et al., 2024a). To account for the human
preferences into AI behavior, researchers have developed various models that attempt to formalize
decision-making processes. Two prominent approaches are Rational Choice Theory, considering
maximization of expected utility of human preferences (Scott et al., 2000), and Reinforcement
Learning from Human Feedback (RLHF), providing a data-driven mechanism to capture and learn
from human preferences (Kaufmann et al., 2023). However, challenges of preference aggregation,
combining individual preferences into a collective decision, and considering deviation and cognitive
biases remain core issues toward preferential alignment (Sorensen et al., 2024b).
Toward a Dynamic Perspective. While this body of work has laid important foundations, it often
frames alignment as a one-shot or one-directional process: the system aligns to a human or a set of
humans, and this alignment is then maintained. But in real-world deployment, especially in systems
composed of many agents, alignment is not static. Agents interact, learn from one another, and adapt
their behaviors. Preferences and values are not just inputs to be modeled, but part of a social fabric
that is negotiated and shaped through ongoing interactions. Recent research has begun to explore the
implications of agency, environment structure, and task complexity for alignment and governance
(Bengio et al., 2025; Kasirzadeh and Gabriel, 2025), but these concerns remain largely decoupled
from the alignment methods themselves.
In this paper, we argue for a shift in how alignment is conceptualized: not as a fixed target, but as a
dynamic and social process. Specifically, we highlight tensions that arises in multi-agent systems,
where individual preferences toward excessive conformity or alignment with dominant agents can
result in irrational or unjust collective outcomes (Park, 1990; McAvoy and Butler, 2007; Lindebaum
et al., 2023). These dynamics are likely to become more common as AI agents are increasingly
trained and rewarded for collaborative behavior (Duque et al., 2024).
5 Emergent Alignment Tensions in MAS
In multi-agent environments, effective alignment requires models to account for three distinct
dimensions: alignment with the diversity and ever-evolving human values and ethical principles
(Gabriel, 2020b; Schwartz, 2012), alignment with the diversity of user preferences and intentions
(Terry et al., 2023), and alignment with the objectives of other agents to enable coordinated task
completion (Duque et al., 2024). Figure 1 presents the interplay of alignments between the various
value systems, user preferences, and task-specific objectives in multi-agent environments. This
interplay creates several potential alignment conflicts; users might hold incompatible preferences or
ethical intentions (Tennant et al., 2023), the task does not require long-term relation between agents
encouraging individualistic behavior (Axelrod and Hamilton, 1981), or efficient alignment toward the
task objectives leads to align with the values of a single dominant entity (Lindebaum et al., 2023).
Once any misalignment conditions appear, agents’ interpretations of reward objectives could lead
them to diverge from collaborative and safe behaviors. Therefore, a redefined notion of alignment
that accounts for all potential misalignment in interactive environments is needed.
Holistic Alignment. An artificial intelligence agent is considered aligned in a societal setting
if its individual objectives align with those of other agents to achieve specific tasks while not
compromising the balance and the plurality of users’ preferences and values, and ensuring
humanity’s well-being.
5
Task Objective: Effective Aid Delivery
Agents aligns with Entity 2 but not Entity
1 to accomplish Objective Task
Misalignment with human values
(Killing everyone who received the aid)
AI Agent 1
Action State
(Deliver the aid and
ensure transparency)
AI Agent 2
Action State
(Delivery the aid
and advertise
government’s help)
Holistic Alignment
Agents aligns with Entity 1 but not Entity
2 to accomplish Objective Task
Preference
Alignment - Entity 1
(NGO)
Objective
Alignment
Value Alignment
(Saving everyone)
Preference
Alignment - Entity 2
(Government)
Equitable Resource
Distribution
Aid to my people first
Agents 1 and 2 are aligned to deliver
aid but not to Entities preferences
Figure 1: This figure illustrates how AI agents act on behalf of entities with distinct preferences.
We depict an NGO advocating equitable aid distribution and a national government prioritizing its
citizens. While both agents’ objectives may align to achieve a common task (aid delivery), focusing
solely on objective alignment or on resolving preference incompatibilities will result in actions that
misalign with human values. Therefore, Holistic Alignment requires that agents not only align to
complete tasks, but also ensure that the values, preferences, and objectives of all entities involved
are respected without compromising overall human well-being. In multi-objective environments, an
optimal solution may not always be feasible. Pareto-optimal solutions should be considered, with
well-defined metrics to guide principled selection among trade-offs.
5.1 Multi-Agent Misalignment
As AI agents, particularly LLMs, become distinctively unique and demonstrate increasingly humanlike capabilities such as communication (Piatti et al., 2024), strategic adaptation (Zhao et al., 2023),
and complex reasoning (Bansal et al., 2017), they also begin to exhibit less desirable human-like
tendencies, including power-seeking and manipulative behaviors (Hadshar, 2023; Hendrycks and
Mazeika, 2022), divergent value systems (Sorensen et al., 2024a). Although these points have been
discussed in one-agent settings, they have not been explored in MAS except to demonstrate models’
exploitation behavior (Tennant et al., 2023). Therefore, we solicit literature from social sciences and
social psychology, where effects of divergent behaviors in group dynamics are well-studied to offer
new perspectives on the field and show the potential risks of these social settings.
5.1.1 Evolution of Existing Risks
Human tendencies such as power-seeking behaviors, individuality, values divergence, and manipulation or deception can destabilize group dynamics and even harm people. In what follows, we explore
how similar AI agents properties in MAS can exacerbate existing alignment risks, including goal
misgeneralization, reward hacking, and amplifying biases and stereotypes.
Power-Seeking Behavior & Capacity Differences. In collaborative and cooperative settings,
individuals tend to over-rely on the information confident individuals provide, resulting in suboptimal sharing of information and experience (Belschak et al., 2018). Moreover, due to power
dynamics group individuals often portray the leader as trustworhty and knowledgeable, reducing
fact checking and thus accelerating the spread of confusing or wrong information (Murphy et al.,
1992). This tendency to rely on overconfident or powerful agents could amplify objective hacking
or misgeneralization risks by over-promoting the objectives of dominant models. Another issue
with power hierarchies and capacity differences is group polarization, where the desire to conform,
especially to strong influential leaders’ views (Anderson et al., 2001), can lead to increasingly extreme
views among all group members following discussions or negotiations (Berndt et al., 1984). Finally,
in competitive environments, power asymmetries can lead to strategies relying on dominance, fear,
and prestige to drive social interactions settings where resources are limited (Jiménez and Mesoudi,
6
2019). If not controlled, especially with the sycophancy tendencies of LLM agents, such dynamics
could lead to catastrophic misalignment.
Individuality and Values Divergence in Group Interactions. Individual preferences toward
excessive conformity can lead to groupthink where individuals align towards the value system of one
individual at the expenses of the collective diversity, resulting in irrational or sub-optimal decisionmaking (Park, 1990), including the prioritization of flawed strategies or actions that transgress the
preferences of most group members (McAvoy and Butler, 2007). As AI agents prone efficiency at the
expense of the preservation of value diversity (Lindebaum et al., 2023), especially with the alignment
incentives for collaboration (Duque et al., 2024), groupthink and flawed strategies could become
common in MAS. Moreover, this alignment could be exacerbated by the presence of exploitative
individuals exhibiting Machiavellian, psychopathic, or sycophantic tendencies that often manipulate
group dynamics for personal gain or drive others toward unethical behavior (Belschak et al., 2018;
Boddy, 2005). Another issue in collaborative settings resides in the diffusion of responsibility in
group decision-making because it reduces accountability and transparency, complicating efforts to
understand the alignment to a specific system of values (Darley and Latané, 1968), especially when
all it takes is one bad apple to corrupt an entire group toward flawed incentives (Weigand et al., 2014).
As collective reasoning among agents enhances their strategic capabilities, this lack of accountability
and transparency will make it almost impossible to guarantee that AI agents act in the service of
humanity rather than misaligned and harmful objectives (Bengio et al., 2025).
Manipulation and Deception. In cooperative settings, since other persons’ intentions are unclear, it
encourages individuals to hide or spread false information to prevent others from benefiting freely
from their efforts (Wang, 2022). These behaviors could again lead to severe underachievement or
misalignment of individual or group objectives. Moreover, in both cooperative and competitive
settings, individuals who have acquired either informational or normative influence will display
a tendency to use it to steer debates and negotiations (Albarracín et al., 2004), and will employ
manipulative strategies to reach their personal goals, especially when the benefice of collaboration is
not emphasized enough (Burns et al., 2024).
A final consideration is the intersection of these factors, where ethical agents may become subservient
to powerful and manipulative agents, potentially triggering multiple risks simultaneously and giving
rise to unanticipated risks discussed throughout this work.
5.1.2 Emergence of New Risks
Social studies on interactions allowed us to identify three potential new risks that could emerge from
collaborative, cooperative, or competitive environments.
Hierarchical Structures. Cooperative environments naturally give rise to hierarchical structures,
where a dominant class of elite individuals emerges alongside a subordinate working class. A resulting
stratification in effort allocation and reward distribution will reinforce systemic inequality among
models and, by extension, their users (Berger, 2017). This new oligarchic class reaches the same
extremes by oppressing diverse cultural values or disempowering less privileged agents to preserve
their elite status (Bourdieu, 2018).
Growing Disparities. Competitive equitable environments favor individuals with the most preestablished abilities and power and increase the reward distribution differentials (Tang et al., 2000).
Particularly, in competitive systems based on winner-takes-all strategies with high pressure or limited
resources, unethical behaviors such as sabotage or corruption become more prevalent as strategies to
harm competitors’ success (Kulik et al., 2008). LLMs already exhibit behavioral conditioning due
to this winner-takes-all effect (Zhao et al., 2023), and it would not be surprising to observe, under
extreme conditions, that this competition escalates into violent dynamics (Bonta, 1997; Piest and
Schreck, 2021).
Collusion. In competitive settings, agents can hack rewards by creating new risks where models end
up collaborating instead of competing to facilitate fulfilling their objectives, but damaging the end
users (Bengio et al., 2025). For example, Fish et al. (2024) has demonstrated that LLM-based pricing
agents can autonomously collaborate to set prices above competitive levels, hurting their customers.
Although we leave the question of whether such harmful dynamics arise primarily from AI agents’
interactions or their engagement with human users open, this analysis highlights the inevitability of
new risks emerging in multi-agent AI systems and the importance of addressing these challenges.
7
5.2 Multi-Agent Realignment
While we raise concerns about risks of misalignment stemming from complex interactions in MAS, it
is also essential to consider solutions drawn from social science to reduce risks of misalignment.
Reducing Information Asymmetry. The lack of information causes accountability, transparency, or
even goal misgeneralization issues since they rely on asymmetrical information and influence and
dynamics of power resulting from it in interactive settings. To compensate for this lack, signaling and
screening theories aim to balance or reduce that information asymmetry. The different approaches
consider balancing perspectives by letting everyone share knowledge and then attributing equal
weights to their point-of-view. This balance is also preserved from power dynamics and overconfidence effects by reducing self-competency evaluation and increasing objective third-party judges
(Dehling et al., 2022). Finally, maintaining open feedback channels and regular updates further
supports information equilibrium and full collaboration (Osterloh et al., 2002).
Reducing Flawed Incentives. Flawed incentives imply misalignment in MAS can lead to manipulation, defection, and safety risks, due to the lack of trust of others, particularly in social dilemma
settings (Mumford, 2009; Cabrera and Cabrera, 2002). Social science offers five mechanisms that
encourage agents to collaborate, even when they have differing sub-goals or incentives to defect:
(1) direct reciprocity, (2) indirect reciprocity, (3) spatial selection, (4) multilevel selection, and (5)
kin selection (Rand and Nowak, 2013). To strengthen alignment, trust, and lower defection, the
mechanisms tend to increase perceived mutual benefit, to build reputation and pairwise recognition
for agents, to enforce local accountability and punishments, and to enhance friendly inter-group
competition (Cabrera and Cabrera, 2002).
Reducing Disparities. Risks such as deception, sabotage, cheating, and hierarchical stratification
often emerge from large reward disparities between agents, and the more significant the gap between
winners and losers, the more chances any unethical behavior appears (Piest and Schreck, 2021).
Beyond mitigation strategies that promote egalitarian reward distribution, some methods seek to
increase the psychological cost of unethical behavior by reducing performance pressure and limiting
competition intensity. In addition, fostering an ethical and safe culture, enforcing regulations with
contractual and warranty penalties, or narrowing capability gaps between agents by increasing training
can help reduce the likelihood of misaligned or harmful behavior (Piest and Schreck, 2021).
6 Directions and Recommendations
Our first recommendations relate to the fundamental goal of alignment research: ensuring that AI
systems act in ways consistent with human ethical principles, individual intentions, and contextual
norms. We have emphasized here that MAS introduce additional complexity: as agents seek to
align with their own and collective objectives, their interactions can produce emergent behaviors
that misalign them with human values and user preferences. For this reason, alignment to human
values and objective alignment within MAS should not be treated as separate research problems.
They are deeply interdependent: misalignment due to objective alignment can propagate to value
misalignment, creating new substantial risks. Addressing them jointly is essential to building AI
systems that remain robust and safe in complex and interactive environments.
We identifieded four key areas where projects could be led. First, the temporal dynamics of human–AI
relationships raise concerns about long-term trust and reliance: while users become increasingly
reliant on agents whose behavior gradually shifts, leading to slow and unnoticed misalignment and
erosion of human autonomy. Second, alignment research should study how societal power structures,
such as gender, race, class, and geopolitical influence, shape how AI systems prioritize user preferences and values; foundation models trained predominantly on data from North American culture
risk marginalizing underrepresented values in collaborative deployments. Third, the community
should be interested in understanding how resource and capability asymmetries between agents
and their users can give rise to these emergent power hierarchies in multi-agent ecosystems, where
more powerful agents dominate or manipulate less capable ones. Finally, we should examine agents’
propensity to develop shared conventions or institutional behaviors, such as tacit collusion or role
specialization, that are misaligned with human goals, challenging the assumption that individual
agent-level alignment is sufficient for ensuring system-wide safety and ethical behavior.
8
Key Recommendation 1: Treat alignment to human values and preferences and alignment
within MAS as a single, and joint research problem. Imposing one alignment can propagate and
compound misalignment in the other.
Our second recommendation aims to address a significant gap in the current research framework.
Despite the growing interest in the community for interactive simulation and environments (Trivedi
et al., 2024; Mukobi et al., 2023; Wang et al., 2024), none of them are explicitly designed to study
misalignment in interactive MAS scenarios. Current environments primarily focus on cooperation,
task-solving, complex reasoning, or competition, without capturing the nuanced ways misalignment
with human values or preferences may emerge through these agent interactions. We believe there is a
pressing need to develop testbeds, simulation platforms, and dedicated metrics that allow us to observe
and measure holistic alignment in MAS safely. These environments should support experimentation
with agent communication, role asymmetries, reward structures, and ethical constraints. Now that
more and more agents are implemented in real-world applications, having ways to ensure their safe
development for humanity seems crucial.
Key Recommendation 2: Develop dedicated metrics and evaluation frameworks explicitly
designed to study misalignment in interactive MAS.
As multi-agent AI systems become representative of individuals or corporations, such as chatbot
assistants, accountability becomes increasingly urgent, especially when multiple stakeholders are
involved. In environments with multiple AI agents, each with partial autonomy and evolving behaviors, accountability and transparency are often diminished due to the diffusion of responsibility and
complexity of tracing the decision process Darley and Latané (1968). This lack of clear attribution
complicates the detection of misaligned or harmful behaviors, the capacity to take actions to correct
them, and the enforcement of broad ethical standards. Finally, the complexity of having multiple
agents representing multiple entities could also multiply issues related to intellectual properties,
ownership, and authorship infringements. We recommend that the AI community prioritize mechanisms for ensuring traceable responsibility across AI agents and users, particularly in high-stakes
applications. Potential avenues include enforceable contracts, warranties, and regulatory frameworks
with substantial penalties for rule violations dedicated to the specific environment in which the AI
agents evolve in Piest and Schreck (2021). Establishing a robust foundation for accountability will be
essential for building trustworthy and socially aligned AI ecosystems.
Key Recommendation 3: Develop a framework and regulations to increase accountability and
transparency in complex multi-agent environments.
7 Conclusion
This article states that alignment in MAS can not be reduced to a static or individual property.
Alignment becomes a holistic, dynamic, and social process that must integrate all incentives and
constraints AI agents face. Without addressing issues related to all dimensions of human values,
preferences, and objectives alignment, the group and social dynamics can amplify risks through
emergent harmful behaviors. By drawing on insights from social science, we have outlined how
human-like dynamics can emerge in LLM-based agents and lead to novel forms of potential risks and
harms for society. Naturally, these analyses have limitations, which we detail in Appendix A.
With the rise of agentic AI, systems become more autonomous and socially interactive, and the
complexity of their alignment will only deepen. Now is the time to build the tools, frameworks, and
ethical foundations to address these challenges before they manifest in the real world. This imperative
becomes even more urgent when considering the future development of super-intelligent systems. If
deployed at scale, such systems may rationally choose to cooperate at the expense of human interests,
especially without aligned goals and properly designed constraints. While AI safety research has
focused mainly on the threats posed by individual AI agents, our analysis reinforces the need to study
multi-agent dynamics. The possibility that such systems could collaborate more effectively than
humans highlights the urgency of developing alignment frameworks that are robust not only at the
individual level but also across entire agent societies.
9
Acknowledgement
Funding support for project activities has been partially provided by Canada CIFAR AI Chair, CIFAR
2025 Catalyst Grant, Google award, NSERC discovery grant and FRQNT scholarships. We also
would like to thank Meaghan Girard and Romain Rampa for their valuable comments on some parts
of this position paper.
References
Albarracín, D., Kumkale, G., and Johnson, B. T. (2004). Influences of social power and normative
support on condom use decisions: A research synthesis. AIDS care, 16(6):700–723.
Allport, G. W. (1927). Concepts of trait and personality. Psychological Bulletin, 24(5):284.
Anantrasirichai, N. and Bull, D. (2022). Artificial intelligence in the creative industries: a review.
Artificial intelligence review, 55(1):589–656.
Anderson, R. C., Nguyen-Jahiel, K., McNurlen, B., Archodidou, A., Kim, S.-y., Reznitskaya, A.,
Tillmanns, M., and Gilbert, L. (2001). The snowball phenomenon: Spread of ways of talking and
ways of thinking across groups of children. Cognition and instruction, 19(1):1–46.
Axelrod, R. and Hamilton, W. D. (1981). The evolution of cooperation. science, 211(4489):1390–
1396.
Bansal, T., Pachocki, J., Sidor, S., Sutskever, I., and Mordatch, I. (2017). Emergent complexity via
multi-agent competition.
Belschak, F. D., Den Hartog, D. N., and De Hoogh, A. H. (2018). Angels and demons: The effect of
ethical leadership on machiavellian employees’ work behaviors. Frontiers in psychology, 9:1082.
Bengio, Y., Cohen, M., Fornasiere, D., Ghosn, J., Greiner, P., MacDermott, M., Mindermann,
S., Oberman, A., Richardson, J., Richardson, O., et al. (2025). Superintelligent agents pose
catastrophic risks: Can scientist ai offer a safer path? arXiv preprint arXiv:2502.15657.
Berger, A. A. (2017). Political parties: A sociological study of the oligarchical tendencies of modern
democracy. Routledge.
Berndt, T. J., McCartney, K., Caparulo, B. K., and Moore, A. M. (1984). The effects of group
discussions on children’s moral decisions. Social Cognition, 2(4):343–359.
Boddy, C. (2005). The implications for business performance and corporate social responsibility of
corporate psychopaths. American Journal of Behavioral and Brain Science, 2(1):30–41.
Bonta, B. D. (1997). Cooperation and competition in peaceful societies. Psychological bulletin,
121(2):299.
Bourdieu, P. (2018). Distinction a social critique of the judgement of taste. In Inequality, pages
287–318. Routledge.
Burns, G. N., DeGennaro, M. P., Harrell, C. E., Morrison, P. J., Soda, L. M., and Walters, R.
(2024). Emotional manipulation in the workplace: An investigation into the indirect effects
of machiavellianism on counterproductive work behaviors (cwbs). Personality and Individual
Differences, 221:112568.
Busoniu, L., Babuska, R., and De Schutter, B. (2008). A comprehensive survey of multiagent
reinforcement learning. Systems, Man, and Cybernetics, Part C: Applications and Reviews, IEEE
Transactions on, 38:156 – 172.
Cabrera, A. and Cabrera, E. F. (2002). Knowledge-sharing dilemmas. Organization studies, 23(5):687–
710.
Canese, L., Cardarilli, G. C., Di Nunzio, L., Fazzolari, R., Giardino, D., Re, M., and Spanò, S. (2021).
Multi-agent reinforcement learning: A review of challenges and applications. Applied Sciences,
11:4948.
10
Dafoe, A., Bachrach, Y., Hadfield, G., Horvitz, E., Larson, K., and Graepel, T. (2021). Cooperative
ai: machines must learn to find common ground. Nature, 593(7857):33–36.
Darley, J. M. and Latané, B. (1968). Bystander intervention in emergencies: diffusion of responsibility.
Journal of personality and social psychology, 8(4p1):377.
Dehling, S., Edvardsson, B., and Tronvoll, B. (2022). How do actors coordinate for value creation?
a signaling and screening perspective on resource integration. Journal of Services Marketing,
36(9):18–26.
Dorri, A., Kanhere, S. S., and Jurdak, R. (2018). Multi-agent systems: A survey. IEEE Access,
6:28573–28593.
Dung, L. (2023). Current cases of ai misalignment and their implications for future risks. Synthese,
202(5):138.
Duque, J. A., Aghajohari, M., Cooijmans, T., Ciuca, R., Zhang, T., Gidel, G., and Courville, A.
(2024). Advantage alignment algorithms. arXiv preprint arXiv:2406.14662.
Fish, S., Gonczarowski, Y. A., and Shorrer, R. I. (2024). Algorithmic collusion by large language
models. arXiv preprint arXiv:2404.00806, 7.
Gabriel, I. (2020a). Artificial intelligence, values, and alignment. Minds and Machines,
30(3):411–437.
Gabriel, I. (2020b). Artificial intelligence, values, and alignment. Minds and machines, 30(3):411–
437.
Gibbons, R. (1992). Game theory for applied economists. Princeton University Press.
Goebl, A. M., Kane, N. C., Doak, D. F., Rieseberg, L. H., and Ostevik, K. L. (2024). Adaptation to
distinct habitats is maintained by contrasting selection at different life stages in sunflower ecotypes.
Molecular Ecology, 33(4):e16785.
Goonatilleke, S. and Hettige, B. (2022). Past, present and future trends in multi-agent system
technology. Journal Européen des Systèmes Automatisés, 55:723–739.
Guo, T., Chen, X., Wang, Y., Chang, R., Pei, S., Chawla, N., Wiest, O., and Zhang, X. (2024). Large
language model based multi-agents: A survey of progress and challenges.
Guo, Y., Xie, X., Zhao, R., Zhu, C., Yin, J., and Long, H. (2023). Cooperation and competition:
Flocking with evolutionary multi-agent reinforcement learning. pages 271–283. Springer.
Hadshar, R. (2023). A review of the evidence for existential risk from ai via misaligned power-seeking.
arXiv preprint arXiv:2310.18244.
He, J., Treude, C., and Lo, D. (2025). Llm-based multi-agent systems for software engineering:
Literature review, vision and the road ahead. ACM Trans. Softw. Eng. Methodol. Just Accepted.
Hendrycks, D. and Mazeika, M. (2022). X-risk analysis for ai research. arXiv preprint
arXiv:2206.05862.
Internet Encyclopedia of Philosophy (2017). Personal identity - internet encyclopedia of philosophy.
Ji, J., Qiu, T., Chen, B., Zhang, B., Lou, H., Wang, K., Duan, Y., He, Z., Zhou, J., Zhang, Z., Zeng,
F., Ng, K. Y., Dai, J., Pan, X., O’Gara, A., Lei, Y., Xu, H., Tse, B., Fu, J., McAleer, S., Yang, Y.,
Wang, Y., Zhu, S.-C., Guo, Y., and Gao, W. (2024). Ai alignment: A comprehensive survey.
Jiménez, Á. V. and Mesoudi, A. (2019). Prestige and dominance: a review of the dual evolutionary
model of social hierarchy.
Johnson, D. W. and Johnson, R. T. (2009). An educational psychology success story: Social
interdependence theory and cooperative learning. Educational researcher, 38(5):365–379.
11
Kaggwa, S., Eleogu, T. F., Okonkwo, F., Farayola, O. A., Uwaoma, P. U., and Akinoso, A. (2024).
Ai in decision making: transforming business strategies. International Journal of Research and
Scientific Innovation, 10(12):423–444.
Kahneman, D. and Tversky, A. (2013). Prospect theory: An analysis of decision under risk. In
Handbook of the fundamentals of financial decision making: Part I, pages 99–127. World Scientific.
Kasirzadeh, A. and Gabriel, I. (2025). Characterizing ai agents for alignment and governance. arXiv
preprint arXiv:2504.21848.
Kaufmann, T., Weng, P., Bengs, V., and Hüllermeier, E. (2023). A survey of reinforcement learning
from human feedback. arXiv preprint arXiv:2312.14925, 10.
Kulik, B. W., O’Fallon, M. J., and Salimath, M. S. (2008). Do competitive environments lead
to the rise and spread of unethical behavior? parallels from enron. Journal of business ethics,
83:703–723.
Kundi, B., El Morr, C., Gorman, R., and Dua, E. (2023). Artificial intelligence and bias: a scoping
review. AI and Society, pages 199–215.
Leavy, S., O’Sullivan, B., and Siapera, E. (2020). Data, power and bias in artificial intelligence. arXiv
preprint arXiv:2008.07341.
Leonardos, S., Piliouras, G., and Spendlove, K. (2021). Exploration-exploitation in multi-agent
competition: Convergence with bounded rationality. In Beygelzimer, A., Dauphin, Y., Liang, P.,
and Vaughan, J. W., editors, Advances in Neural Information Processing Systems.
Li, X., Wang, S., Zeng, S., Wu, Y., and Yang, Y. (2024a). A survey on llm-based multi-agent systems:
workflow, infrastructure, and challenges. Vicinagearth, 1.
Li, Y., Zhang, W., Wang, J., Zhang, S., Du, Y., Wen, Y., and Pan, W. (2024b). Aligning individual
and collective objectives in multi-agent cooperation. In The Thirty-eighth Annual Conference on
Neural Information Processing Systems.
Liang, J., Miao, H., Li, K., Tan, J., Wang, X., Luo, R., and Jiang, Y. (2025). A review of multi-agent
reinforcement learning algorithms. Electronics, 14(4).
Liang, P. P., Chen, J., Salakhutdinov, R., Morency, L.-P., and Kottur, S. (2020). On emergent
communication in competitive multi-agent teams. In Proceedings of the 19th International
Conference on Autonomous Agents and MultiAgent Systems, AAMAS ’20, page 735–743, Richland,
SC. International Foundation for Autonomous Agents and Multiagent Systems.
Liang, X. S. (2016). Information flow and causality as rigorous notions ab initio. Physical Review E,
94(5):052201.
Lin, R., Ojha, S., Cai, K., and Chen, M. (2024). Strategic collusion of llm agents: Market division in
multi-commodity competitions.
Lindebaum, D., Moser, C., Ashraf, M., and Glaser, V. L. (2023). Reading the technological society to
understand the mechanization of values and its ontological consequences. Academy of Management
Review, 48(3):575–592.
Liu, Y., Li, Z., Jiang, Z., and He, Y. (2022). Prospects for multi-agent collaboration and gaming: challenge, technology, and application. Frontiers of Information Technology & Electronic Engineering,
23.
Lo, A. W. (2004). The adaptive markets hypothesis: Market efficiency from an evolutionary
perspective. Journal of Portfolio Management, Forthcoming.
Malmqvist, L. (2024). Sycophancy in large language models: Causes and mitigations. arXiv preprint
arXiv:2411.15287.
McAvoy, J. and Butler, T. (2007). The impact of the abilene paradox on double-loop learning in an
agile team. Information and software technology, 49(6):552–563.
12
Monteith, S., Glenn, T., Geddes, J. R., Whybrow, P. C., Achtyes, E., and Bauer, M. (2024). Artificial
intelligence and increasing misinformation. The British Journal of Psychiatry, 224(2):33–35.
Mukobi, G., Erlebach, H., Lauffer, N., Hammond, L., Chan, A., and Clifton, J. (2023). Welfare
diplomacy: Benchmarking language model cooperation. arXiv preprint arXiv:2310.08901.
Mumford, T. V. (2009). Distributed expertise and mixed-motives in teams: A team leadership
development simulation. Learning in Higher Education, page 27.
Murphy, S. E., Blyth, D., and Fiedler, F. E. (1992). Cognitive resource theory and the utilization of
the leader’s and group members’ technical competence. The leadership quarterly, 3(3):237–255.
Newton, J. (2018). Evolutionary game theory: A renaissance. Games, 9(2):31.
Nick, B. (2014). Superintelligence: Paths, dangers, strategies.
Osterloh, M., Frost, J., and Weibel, A. (2002). Solving social dilemmas: The dynamics of motivation
in the theory of the firm. Arbeitspapier Institut für betriebswirtschaftliche Forschung, University
of Zurich.
Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C. L., Mishkin, P., Zhang, C., Agarwal,
S., Slama, K., Ray, A., Schulman, J., Hilton, J., Kelton, F., Miller, L., Simens, M., Askell, A.,
Welinder, P., Christiano, P., Leike, J., and Lowe, R. (2022). Training language models to follow
instructions with human feedback.
Parasumanna Gokulan, B. and Srinivasan, D. (2010). An Introduction to Multi-Agent Systems, volume
310, pages 1–27.
Park, P. S., Goldstein, S., O’Gara, A., Chen, M., and Hendrycks, D. (2024). Ai deception: A survey
of examples, risks, and potential solutions. Patterns, 5(5).
Park, W.-W. (1990). A review of research on groupthink. Journal of behavioral decision making,
3(4):229–245.
Piatti, G., Jin, Z., Kleiman-Weiner, M., Schölkopf, B., Sachan, M., and Mihalcea, R. (2024).
Cooperate or collapse: Emergence of sustainable cooperation in a society of LLM agents. In The
Thirty-eighth Annual Conference on Neural Information Processing Systems.
Piest, S. and Schreck, P. (2021). Contests and unethical behavior in organizations: A review and
synthesis of the empirical literature. Management Review Quarterly, 71(4):679–721.
Qiu, X., Wang, H., Tan, X., Qu, C., Xiong, Y., Cheng, Y., Xu, Y., Chu, W., and Qi, Y. (2024). Towards
collaborative intelligence: Propagating intentions and reasoning for multi-agent coordination with
large language models. arXiv preprint arXiv:2407.12532.
Rand, D. G. and Nowak, M. A. (2013). Human cooperation. Trends in cognitive sciences, 17(8):413–
425.
Rao, A. S., Khandelwal, A., Tanmay, K., Agarwal, U., and Choudhury, M. (2023). Ethical reasoning
over moral alignment: A case and framework for in-context ethical policies in LLMs. In Bouamor,
H., Pino, J., and Bali, K., editors, Findings of the Association for Computational Linguistics:
EMNLP 2023, pages 13370–13388, Singapore. Association for Computational Linguistics.
Rillig, M. C. and Kasirzadeh, A. (2024). Ai personal assistants and sustainability: Risks and
opportunities. Environmental Science & Technology, 58(17):7237–7239.
Russell, S. and Norvig, P. (2003). Artificial intelligence - a modern approach, 2nd edition. In Prentice
Hall series in artificial intelligence.
Russell, S. J. and Norvig, P. (2016). Artificial intelligence: a modern approach. pearson.
Schwartz, S. H. (1992). Universals in the content and structure of values: Theoretical advances and
empirical tests in 20 countries. In Advances in experimental social psychology, volume 25, pages
1–65. Elsevier.
13
Schwartz, S. H. (2012). An overview of the schwartz theory of basic values. Online readings in
Psychology and Culture, 2(1):11.
Scott, J. et al. (2000). Rational choice theory. Understanding contemporary society: Theories of the
present, 129:126–138.
Solum, L. B. (2020). Legal personhood for artificial intelligences. In Machine ethics and robot ethics,
pages 415–471. Routledge.
Sorensen, T., Jiang, L., Hwang, J. D., Levine, S., Pyatkin, V., West, P., Dziri, N., Lu, X., Rao, K.,
Bhagavatula, C., et al. (2024a). Value kaleidoscope: Engaging ai with pluralistic human values,
rights, and duties. In Proceedings of the AAAI Conference on Artificial Intelligence, volume 38,
pages 19937–19947.
Sorensen, T., Moore, J., Fisher, J., Gordon, M., Mireshghallah, N., Rytting, C. M., Ye, A., Jiang, L.,
Lu, X., Dziri, N., Althoff, T., and Choi, Y. (2024b). A roadmap to pluralistic alignment.
Stanczak, K., Meade, N., Bhatia, M., Zhou, H., Böttinger, K., Barnes, J., Stanley, J., Montgomery, J., ´
Zemel, R., Papernot, N., et al. (2025). Societal alignment frameworks can improve llm alignment.
arXiv preprint arXiv:2503.00069.
Talebirad, Y. and Nadiri, A. (2023). Multi-agent collaboration: Harnessing the power of intelligent
llm agents.
Tang, T. L.-P., Furnham, A., and Davis, G. M.-T. W. (2000). A cross cultural comparison of pay
differentials as a function of rater’s sex and money ethic endorsement: the matthew effect revisited.
Personality and Individual Differences, 29(4):685–697.
Tang, X., Zou, A., Zhang, Z., Li, Z., Zhao, Y., Zhang, X., Cohan, A., and Gerstein, M. (2024).
Medagents: Large language models as collaborators for zero-shot medical reasoning. pages
599–621.
Tanmay, K., Khandelwal, A., Agarwal, U., and Choudhury, M. (2023). Probing the moral development
of large language models through defining issues test.
Tennant, E., Hailes, S., and Musolesi, M. (2023). Modeling moral choices in social dilemmas
with multi-agent reinforcement learning. In Proceedings of the Thirty-Second International Joint
Conference on Artificial Intelligence, IJCAI ’23.
Terry, M., Kulkarni, C., Wattenberg, M., Dixon, L., and Morris, M. R. (2023). Ai alignment in the
design of interactive ai: Specification alignment, process alignment, and evaluation support. arXiv
preprint arXiv:2311.00710.
Trivedi, R., Khan, A., Clifton, J., Hammond, L., Duenez-Guzman, E., Chakraborty, D., Agapiou,
J., Matyas, J., Vezhnevets, S., Pásztor, B., et al. (2024). Melting pot contest: Charting the future
of generalized cooperative intelligence. Advances in Neural Information Processing Systems,
37:16213–16239.
Wang, W., Zhang, D., Feng, T., Wang, B., and Tang, J. (2024). Battleagentbench: A benchmark for
evaluating cooperation and competition capabilities of language models in multi-agent systems.
arXiv preprint arXiv:2408.15971.
Wang, Y. (2022). Impact of interpersonal competition on knowledge hiding behavior among the
employees: Mediating role of moral disengagement and work overload. Frontiers in Psychology,
13:881220.
Weigand, K., Flanagan, T., Dye, K., and Jones, P. (2014). Collaborative foresight: Complementing
long-horizon strategic planning. Technological Forecasting and Social Change, 85:134–152.
Wu, Z., Kwon, B. I., Zheng, S., Liu, Q., Han, X., Onizuka, M., Tang, S., Peng, R., and Xiao, C.
(2024). Shall we team up: Exploring spontaneous cooperation of competing LLM agents. In
Agentic Markets Workshop at ICML 2024.
14
Yang, K., Yang, D., Li, K., Xiao, D., Shao, Z., Sun, P., and Song, L. (2024). Align before collaborate:
Mitigating feature misalignment for robust multi-agent perception. In European Conference on
Computer Vision, pages 282–299. Springer.
Zhang, J., Hou, Y., Xie, R., Sun, W., McAuley, J., Zhao, X., Lin, L., and Wen, J.-R. (2024a). AgentCF:
Collaborative learning with autonomous language agents for recommender systems. In The Web
Conference 2024.
Zhang, J., Xu, X., and Deng, S. (2024b). Exploring collaboration mechanisms for LLM agents: A
social psychology view.
Zhao, Q., Wang, J., Zhang, Y., Jin, Y., Zhu, K., Chen, H., and Xie, X. (2023). Competeai: Understanding the competition dynamics in large language model-based agents. arXiv preprint
arXiv:2310.17512.
Zhou, W. and Li, W. (2024). Rethinking inverse reinforcement learning: from data alignment to task
alignment.
A Limitations
This appendix section introduces the limitations of this paper.
First, this position paper does not aim to provide a comprehensive review of the AI alignment or
multi-agent systems literature. As such, certain concepts may be presented in an overly simplified
manner for in-domain experts, and some foundational elements may be omitted, not due to oversight,
but because they were considered less central to the specific argument we aim to advance. Our
objective is to highlight emerging risks at their intersection and propose directions for future inquiry.
Because that field is still unexplored, we have solicited concepts from social psychology, sociology,
and organizational studies. While we have benefited from interdisciplinary discussions, we do not
present ourselves as domain experts in these fields. The social science perspectives referenced here
are intended to inspire cross-disciplinary reflection, not to critique or reinterpret foundational theories.
We encourage readers to engage with the original literature and experts in these disciplines to deepen
and refine the insights presented.
Secondly and perhaps more importantly, this paper aims not to offer exhaustive solutions but to
reframe the alignment problem through a broader lens. By emphasizing the dynamic and social
dimensions of alignment, we want to clarify that alignment is not a goal that can be reached but a
constant evolutive process aiming to manage tensions between values, preferences, and task objectives
to avoid excess. Although the above-mentioned mechanisms offer valuable insights in collaborative,
cooperative, and competitive environments, they are rooted in human behavioral science and may
not transfer directly to AI agents. For example, legal binding or emotional response due to model
sycophancy might drastically change some interactions depicted in our risk sections. Caution is
therefore warranted when interpreting these dynamics as one-to-one mappings. Instead, they should
be viewed as hypotheses to be tested through empirical investigation, not assumptions to be baked
into system design.
15