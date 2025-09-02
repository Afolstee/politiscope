"use client"

import type React from "react"
import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { Upload, FileText, Download, Brain, Loader2, Settings, Eye, EyeOff } from "lucide-react"

export default function DiscourseAnalysisPage() {
  const [inputText, setInputText] = useState("")
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState("")
  const [activeTab, setActiveTab] = useState("input")
  const [apiKey, setApiKey] = useState("")
  const [showApiKey, setShowApiKey] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [analysisStatus, setAnalysisStatus] = useState("")
  const [selectedModel, setSelectedModel] = useState("")

  const handleAnalyze = async () => {
    if (!inputText.trim()) return

    const wordCount = inputText.trim().split(/\s+/).length
    if (wordCount > 4000) {
      alert("Text exceeds 4000 words limit. Please shorten your text.")
      return
    }

    setIsAnalyzing(true)
    setAnalysisResult("")
    setActiveTab("results")
    setAnalysisProgress(0)
    setAnalysisStatus("Selecting appropriate CDA model...")
    setSelectedModel("")

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: inputText, apiKey: apiKey.trim() || undefined }),
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(errorText || "Failed to analyze text")
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let fullResponse = ""
      let progressStage = 0 // 0: model selection, 1: textual analysis, 2: discursive analysis, 3: completion

      if (reader) {
        setAnalysisProgress(10)

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value, { stream: true })
          fullResponse += chunk

          if (
            progressStage === 0 &&
            ((!selectedModel && fullResponse.includes("Selected CDA Model")) ||
              fullResponse.includes("CDA Model Selection") ||
              fullResponse.includes("Fairclough") ||
              fullResponse.includes("van Dijk") ||
              fullResponse.includes("Wodak"))
          ) {
            let modelName = "CDA Model"
            if (fullResponse.toLowerCase().includes("fairclough")) {
              modelName = "Fairclough's Three-Dimensional Framework"
            } else if (
              fullResponse.toLowerCase().includes("van dijk") ||
              fullResponse.toLowerCase().includes("van-dijk")
            ) {
              modelName = "van Dijk's Socio-Cognitive Approach"
            } else if (fullResponse.toLowerCase().includes("wodak")) {
              modelName = "Wodak's Discourse-Historical Approach"
            } else if (
              fullResponse.toLowerCase().includes("three-dimensional") ||
              fullResponse.toLowerCase().includes("textual analysis")
            ) {
              modelName = "Fairclough's Three-Dimensional Framework"
            } else if (
              fullResponse.toLowerCase().includes("socio-cognitive") ||
              fullResponse.toLowerCase().includes("mental model")
            ) {
              modelName = "van Dijk's Socio-Cognitive Approach"
            } else if (
              fullResponse.toLowerCase().includes("discourse-historical") ||
              fullResponse.toLowerCase().includes("historical context")
            ) {
              modelName = "Wodak's Discourse-Historical Approach"
            }

            setSelectedModel(modelName)
            setAnalysisStatus(`Selected: ${modelName} - Conducting textual analysis...`)
            setAnalysisProgress(30)
            progressStage = 1
          } else if (
            progressStage === 1 &&
            (fullResponse.includes("Textual Analysis") || fullResponse.includes("Text Analysis"))
          ) {
            setAnalysisStatus(`${selectedModel} - Analyzing discursive practices...`)
            setAnalysisProgress(50)
            progressStage = 2
          } else if (
            progressStage === 2 &&
            (fullResponse.includes("Discursive Practice") || fullResponse.includes("Social Practice"))
          ) {
            setAnalysisStatus(`${selectedModel} - Examining social implications...`)
            setAnalysisProgress(70)
            progressStage = 3
          } else if (
            progressStage === 3 &&
            (fullResponse.includes("Social Implications") || fullResponse.includes("Conclusion"))
          ) {
            setAnalysisStatus(`${selectedModel} - Finalizing analysis...`)
            setAnalysisProgress(90)
          }

          const cleanedResponse = fullResponse
            .replace(/\*\*(.*?)\*\*/g, "$1")
            .replace(/\*([^*]+)\*/g, "$1")
            .replace(/(?:As an AI|I am an AI|This analysis was generated by|AI-generated|Generated by AI)[^.]*\./gi, "")
            .replace(/(?:Please note that this is an AI analysis|This AI analysis|AI disclaimer)[^.]*\./gi, "")
            .trim()

          setAnalysisResult(cleanedResponse)
        }

        setAnalysisProgress(100)
        setAnalysisStatus(`Analysis complete using ${selectedModel}`)

        await new Promise((resolve) => setTimeout(resolve, 1000))
      }
    } catch (error) {
      console.error("Analysis error:", error)
      setAnalysisResult(
        `Error: ${error instanceof Error ? error.message : "Failed to analyze text. Please try again."}`,
      )
      setAnalysisProgress(0)
      setAnalysisStatus("Analysis failed")
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file && file.type === "text/plain") {
      const reader = new FileReader()
      reader.onload = (e) => {
        const text = e.target?.result as string
        const wordCount = text.trim().split(/\s+/).length
        if (wordCount > 4000) {
          alert("File exceeds 4000 words limit. Please use a shorter text.")
          return
        }
        setInputText(text)
      }
      reader.readAsText(file)
    }
  }

  const handleDownloadPDF = () => {
    if (!analysisResult) return

    const cleanContent = `
CRITICAL DISCOURSE ANALYSIS REPORT

ORIGINAL TEXT:
${inputText}

ANALYSIS:
${analysisResult}

Generated on: ${new Date().toLocaleDateString()}
    `.trim()

    const blob = new Blob([cleanContent], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "discourse-analysis-report.txt"
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const wordCount = inputText
    .trim()
    .split(/\s+/)
    .filter((word) => word.length > 0).length
  const isOverLimit = wordCount > 4000

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-cyan-50">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Brain className="h-8 w-8 text-cyan-600" />
            <h1 className="text-4xl font-bold text-slate-900">Critical Discourse Analysis</h1>
          </div>
          <p className="text-lg text-slate-600 max-w-3xl mx-auto">
            Advanced system that dynamically selects appropriate CDA models and provides comprehensive discourse
            analysis
          </p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="max-w-6xl mx-auto">
          <TabsList className="grid w-full grid-cols-4 mb-8">
            <TabsTrigger value="input" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Text Input
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Settings
            </TabsTrigger>
            <TabsTrigger value="results" className="flex items-center gap-2">
              <Brain className="h-4 w-4" />
              Analysis
            </TabsTrigger>
            <TabsTrigger value="export" className="flex items-center gap-2">
              <Download className="h-4 w-4" />
              Export
            </TabsTrigger>
          </TabsList>

          <TabsContent value="input" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-cyan-600" />
                  Text Input
                </CardTitle>
                <CardDescription>
                  Enter or upload text for Critical Discourse Analysis (Maximum 4000 words)
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Textarea
                    placeholder="Paste your text here for comprehensive discourse analysis..."
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    className="min-h-[300px] resize-none"
                  />
                  <div className="flex justify-between items-center text-sm">
                    <span className={`${isOverLimit ? "text-red-600" : "text-slate-600"}`}>
                      {wordCount} / 4000 words
                    </span>
                    {isOverLimit && <span className="text-red-600 font-medium">Text exceeds limit</span>}
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <Upload className="h-4 w-4 text-slate-600" />
                    <label htmlFor="file-upload" className="cursor-pointer text-sm text-slate-600 hover:text-cyan-600">
                      Upload .txt file
                    </label>
                    <input id="file-upload" type="file" accept=".txt" onChange={handleFileUpload} className="hidden" />
                  </div>
                </div>

                <Button
                  onClick={handleAnalyze}
                  disabled={!inputText.trim() || isOverLimit || isAnalyzing}
                  className="w-full bg-cyan-600 hover:bg-cyan-700"
                  size="lg"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Brain className="h-4 w-4 mr-2" />
                      Analyze Text
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="settings" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5 text-cyan-600" />
                  API Configuration
                </CardTitle>
                <CardDescription>
                  Configure your xAI API key for discourse analysis (optional if environment variable is set)
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label htmlFor="api-key" className="text-sm font-medium text-slate-700">
                    xAI API Key
                  </label>
                  <div className="relative">
                    <Input
                      id="api-key"
                      type={showApiKey ? "text" : "password"}
                      placeholder="Enter your xAI API key (optional)"
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      className="pr-10"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                      onClick={() => setShowApiKey(!showApiKey)}
                    >
                      {showApiKey ? (
                        <EyeOff className="h-4 w-4 text-slate-400" />
                      ) : (
                        <Eye className="h-4 w-4 text-slate-400" />
                      )}
                    </Button>
                  </div>
                  <p className="text-xs text-slate-500">
                    If you're experiencing API key errors, enter your xAI API key here. Get one from{" "}
                    <a
                      href="https://console.x.ai"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-cyan-600 hover:underline"
                    >
                      console.x.ai
                    </a>
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="results" className="space-y-6">
            {isAnalyzing ? (
              <Card>
                <CardContent className="p-8">
                  <div className="text-center mb-6">
                    <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-cyan-600" />
                    <h3 className="text-lg font-semibold mb-2">Analysis in Progress</h3>
                    <p className="text-slate-600 mb-4">{analysisStatus}</p>

                    <div className="max-w-md mx-auto">
                      <Progress value={analysisProgress} className="mb-2" />
                      <p className="text-sm text-slate-500">{analysisProgress}% complete</p>
                    </div>

                    {selectedModel && (
                      <div className="mt-4 p-3 bg-cyan-50 rounded-lg border border-cyan-200">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-cyan-600 rounded-full"></div>
                          <p className="text-sm font-medium text-cyan-800">Selected Model: {selectedModel}</p>
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ) : analysisResult ? (
              <>
                <Card>
                  <CardHeader>
                    <CardTitle>Original Text</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="bg-slate-50 p-4 rounded-lg">
                      <p className="text-slate-700 whitespace-pre-wrap">{inputText}</p>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Brain className="h-5 w-5 text-cyan-600" />
                      Critical Discourse Analysis
                    </CardTitle>
                    <CardDescription>Comprehensive analysis using dynamically selected CDA methodology</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="prose max-w-none">
                      <div className="whitespace-pre-wrap text-slate-700 leading-relaxed">{analysisResult}</div>
                    </div>
                  </CardContent>
                </Card>
              </>
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <Brain className="h-8 w-8 mx-auto mb-4 text-slate-400" />
                  <h3 className="text-lg font-semibold mb-2">No Analysis Yet</h3>
                  <p className="text-slate-600">Enter text in the input tab and click "Analyze Text" to begin.</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="export" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Download className="h-5 w-5 text-cyan-600" />
                  Export Analysis
                </CardTitle>
                <CardDescription>Download your discourse analysis report</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button
                  onClick={handleDownloadPDF}
                  disabled={!analysisResult}
                  className="w-full bg-transparent"
                  variant="outline"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download Analysis Report (.txt)
                </Button>

                {!analysisResult && (
                  <p className="text-sm text-slate-500 text-center">
                    Complete an analysis first to enable export functionality
                  </p>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
