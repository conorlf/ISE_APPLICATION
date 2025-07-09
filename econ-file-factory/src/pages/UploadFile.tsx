import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Upload, FileText, ArrowLeft, ArrowRight } from "lucide-react";
import NavBar from "@/components/NavBar";
import InstructionsCardComponent from "@/components/instructionsCard";
import Footer from "@/components/Footer";
import FileUploader from "@/components/FileUploader";
import DataPreview from "@/components/DataPreview";
import HeaderMapping from "@/components/HeaderMapping";
import RegressionOptions from "@/components/RegressionOptions";
import FileGenerator from "@/components/FileGenerator";
import { useToast } from "@/hooks/use-toast";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import ReturnDataPreview from "@/components/returnDataPreview";

const UploadFile = () => {
  const { toast } = useToast();
  const [fileData, setFileData] = useState<any>(null);
  const [headers, setHeaders] = useState<string[]>([]);
  const [previewData, setPreviewData] = useState<any[]>([]);
  const [headerMapping, setHeaderMapping] = useState<Record<string, string>>({});
  const [regressionOptions, setRegressionOptions] = useState({
    type: "OLS",
    robustSE: false,
    clustering: false,
    clusterVariable: "",
    timeTrends: false,
    fixedEffects: [],
  });
  const [activeTab, setActiveTab] = useState("upload");
  const [isReady, setIsReady] = useState({
    upload: false,
    preview: false,
    mapping: false,
    options: false,
  });
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [wrangledData, setWrangledData] = useState<any[]>([]);
  const [wrangledHeaders, setWrangledHeaders] = useState<string[]>([]);

  useEffect(() => {
    if (isReady.upload) {
      setActiveTab("preview");
    }
  }, [isReady.upload]);

  const handleDataParsed = (data: any, headers: string[], preview: any[]) => {
    setFileData(data);
    setHeaders(headers);
    setPreviewData(preview);
    setIsReady(prev => ({ ...prev, upload: true }));
    toast({
      title: "File Uploaded Successfully",
      description: `Found ${headers.length} columns and ${data.length} rows`,
    });
  };

  const handleMappingComplete = (mapping: Record<string, string>) => {
    setHeaderMapping(mapping);
    setIsReady({ ...isReady, mapping: true });
    toast({
      title: "Header Mapping Complete",
      description: "Your variables have been mapped successfully",
    });
    setActiveTab("options");
  };

  const handleRegressionOptionsComplete = (options: any) => {
    setRegressionOptions(options);
    setIsReady({ ...isReady, options: true });
    toast({
      title: "Regression Options Set",
      description: "Your regression options have been saved",
    });
    setActiveTab("generate");
  };

  const handleGoToMapping = () => {
    setIsReady(prev => ({ ...prev, preview: true }));
    setActiveTab("mapping");
  };

  const handleFilesSelected = (files: File[]) => {
    setSelectedFiles(files);
    setActiveTab("preview");
  };

  const handleWrangledDataReady = (data: any[], headers: string[]) => {
    setWrangledData(data);
    setWrangledHeaders(headers);
    setIsReady(prev => ({ ...prev, preview: true }));
    setActiveTab("mapping");
    toast({
      title: "Files Combined",
      description: `Wrangled file has ${headers.length} columns and ${data.length} rows. Ready for mapping.`,
    });
  };

  console.log("activeTab", activeTab);
  console.log("isReady", isReady);

  return (
    <div className="min-h-screen flex flex-col ">
      <NavBar />
      <main className="flex-grow container mx-auto px-4 py-8 fadeIn">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-primary mb-2">File(s) Processor</h1>
          
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-8">
          <TabsList className="grid w-full grid-cols-5 max-w-full">
            <TabsTrigger value="upload" disabled={false}>1. Upload</TabsTrigger>
            <TabsTrigger value="preview" disabled={selectedFiles.length === 0}>2. Preview</TabsTrigger>
            <TabsTrigger value="mapping" disabled={!isReady.preview}>3. Map Headers</TabsTrigger>
            <TabsTrigger value="options" disabled={!isReady.mapping}>4. Regression Options</TabsTrigger>
            <TabsTrigger value="generate" disabled={!isReady.options}>5. Generate Files</TabsTrigger>
          </TabsList>

          <TabsContent value="upload" className="space-y-4">
            <div className="bg-white rounded-lg p-6 shadow-md">
              <FileUploader onFilesSelected={handleFilesSelected} />
              <InstructionsCardComponent></InstructionsCardComponent>
            </div>
          </TabsContent>

          <TabsContent value="preview" className="space-y-4">
            <div className="bg-white rounded-lg p-6 shadow-md">
              {selectedFiles.length > 0 && (
                <DataPreview
                  files={selectedFiles} 
                  onBackToUpload={() => setActiveTab("upload")}
                  onGoToMapping={handleGoToMapping}
                  onWrangledDataReady={handleWrangledDataReady}
                  onContinue={handleGoToMapping}
                />
              )}
            </div>
          </TabsContent>

          <TabsContent value="mapping" className="space-y-4">
            <div className="bg-white rounded-lg p-6 shadow-md">
              <ReturnDataPreview headers={wrangledHeaders.length > 0 ? wrangledHeaders : headers} data={wrangledData} />
              <HeaderMapping 
                headers={wrangledHeaders.length > 0 ? wrangledHeaders : headers} 
                onMappingComplete={handleMappingComplete} 
              />
            </div>
          </TabsContent>

          <TabsContent value="options" className="space-y-4">
            <div className="bg-white rounded-lg p-6 shadow-md">
              <RegressionOptions 
                headers={headers} 
                headerMapping={headerMapping}
                onOptionsComplete={handleRegressionOptionsComplete} 
              />
            </div>
          </TabsContent>

          <TabsContent value="generate" className="space-y-4">
            <div className="bg-white rounded-lg p-6 shadow-md">
              <FileGenerator 
                data={wrangledData.length > 0 ? wrangledData : fileData} 
                headers={wrangledHeaders.length > 0 ? wrangledHeaders : headers}
                headerMapping={headerMapping}
                regressionOptions={regressionOptions}
                onBack={() => setActiveTab("options")}
                onReset={() => {
                  setActiveTab("upload");
                  setFileData(null);
                  setHeaders([]);
                  setPreviewData([]);
                  setHeaderMapping({});
                  setRegressionOptions({
                    type: "OLS",
                    robustSE: false,
                    clustering: false,
                    clusterVariable: "",
                    timeTrends: false,
                    fixedEffects: [],
                  });
                  setSelectedFiles([]);
                  setWrangledData([]);
                  setWrangledHeaders([]);
                  setIsReady({
                    upload: false,
                    preview: false,
                    mapping: false,
                    options: false,
                  });
                }}
              />
            </div>
          </TabsContent>
        </Tabs>
      </main>
      <Footer />
    </div>
  );
};

export default UploadFile;
