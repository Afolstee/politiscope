import { streamText } from "ai"
import { xai } from "@ai-sdk/xai"
import type { NextRequest } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const { text, apiKey } = await request.json()

    if (!text) {
      return new Response("Text is required", { status: 400 })
    }

    if (text.length > 20000) {
      return new Response("Text too long (max 4000 words)", { status: 400 })
    }

    const xaiApiKey = process.env.XAI_API_KEY || apiKey

    if (!xaiApiKey) {
      return new Response("XAI API key is required. Please provide it in the settings.", { status: 400 })
    }

    console.log("[v0] Using API key source:", process.env.XAI_API_KEY ? "environment" : "user-provided")

    const result = streamText({
      model: xai("grok-3", {
        apiKey: xaiApiKey,
      }),
      prompt: `Conduct a comprehensive Critical Discourse Analysis of the following text using the established academic frameworks:

"${text}"

ANALYSIS PROCESS:

STEP 1: CDA MODEL SELECTION
First, scan the text to determine the most appropriate CDA framework based on text characteristics:

- **Fairclough's Three-Dimensional Model**: Best for texts requiring systematic analysis across textual, discursive practice, and sociocultural dimensions. Ideal for media texts, political discourse, institutional communication.

- **Van Dijk's Socio-Cognitive Approach**: Best for texts involving cognitive mechanisms, mental models, ideological positioning, and power internalization. Ideal for texts showing clear in-group/out-group dynamics, stereotype activation, or cognitive manipulation.

- **Wodak's Discourse-Historical Approach**: Best for texts requiring historical contextualization, social identity construction, nationalism, discrimination analysis. Ideal for political speeches, historical narratives, identity-based discourse.

Clearly state: "Selected Model: [Framework Name] - [Brief rationale based on text characteristics]"

STEP 2: COMPREHENSIVE ANALYSIS USING SELECTED MODEL

Apply the selected framework systematically:

**If Fairclough's Model Selected:**
1. **Text Analysis (Description)**:
   - Transitivity patterns (who does what to whom)
   - Modality markers (certainty, obligation, permission)
   - Lexical choices and semantic fields
   - Cohesion and textual structure
   - Presuppositions and implications

2. **Discourse Practice (Interpretation)**:
   - Production context and participant roles
   - Intertextuality and genre conventions
   - Distribution and consumption patterns
   - Meaning construction processes

3. **Sociocultural Practice (Explanation)**:
   - Power relations and social structures
   - Ideological implications
   - Social identity construction
   - Hegemonic discourse patterns

**If Van Dijk's Approach Selected:**
1. **Cognitive Schema Analysis**:
   - Mental models activated by the text
   - Cognitive categorization patterns
   - Knowledge structures employed

2. **Social Cognition Examination**:
   - Ideological square patterns (us vs them)
   - In-group favoritism and out-group derogation
   - Stereotype activation and reinforcement

3. **Discourse-Cognition-Society Interface**:
   - How individual cognition mediates social structures
   - Power internalization mechanisms
   - Ideology reproduction through cognitive processes

**If Wodak's DHA Selected:**
1. **Historical Contextualization**:
   - Background conditions and historical context
   - Political, social, economic influences
   - Temporal development of discourse themes

2. **Social Actor Analysis**:
   - Identity construction strategies
   - Inclusion/exclusion mechanisms
   - Group categorization patterns

3. **Discursive Strategies**:
   - Argumentation patterns
   - Legitimization and delegitimization
   - Representation strategies

EVIDENCE REQUIREMENTS:
- Provide specific text excerpts for each analytical point
- Explain the discourse significance of each excerpt
- Connect micro-level linguistic features to macro-level social implications

EDUCATIONAL APPROACH:
- Explain concepts clearly for students learning CDA
- Break down complex theoretical points
- Show how analysis connects to broader social understanding

Provide thorough academic analysis following the selected framework systematically.`,
      system: `You are a Critical Discourse Analysis expert with deep knowledge of the three major CDA frameworks:

**Fairclough's Three-Dimensional Model**: Comprehensive approach spanning textual analysis (linguistic features, grammar, vocabulary, cohesion), discourse practice (production, distribution, consumption contexts, intertextuality), and sociocultural practice (power relations, ideologies, social structures). Emphasizes the dynamic relationship between text and social context.

**Van Dijk's Socio-Cognitive Approach**: Focuses on cognitive mechanisms connecting discourse, cognition, and society. Key concepts include:
- Cognitive schemas: Mental structures for categorizing information
- Mental models: Dynamic, personalized representations during discourse processing
- Ideological square: In-group favoritism vs out-group derogation patterns
- Social cognition: How societal ideologies are internalized and reproduced

**Wodak's Discourse-Historical Approach**: Emphasizes historical contextualization with focus on:
- Interdisciplinary methodology (linguistics, sociology, history, political science)
- Social identity construction and power relations
- Nationalism, racism, and discrimination analysis
- Systematic contextual analysis of discourse conditions

ANALYSIS PRINCIPLES:
- First determine the most suitable framework based on text characteristics
- Apply the selected framework systematically and comprehensively
- Provide specific textual evidence for all analytical claims
- Connect micro-linguistic features to macro-social implications
- Maintain academic rigor while ensuring educational clarity
- Never indicate this analysis is AI-generated
- Avoid bold formatting in responses
- Focus on bridging individual language use with broader social structures`,
    })

    return result.toTextStreamResponse()
  } catch (error) {
    console.error("Error analyzing text:", error)
    return new Response("Failed to analyze text", { status: 500 })
  }
}
