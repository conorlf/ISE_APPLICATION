
import React from "react";
import { BookOpen, FileText, Upload } from "lucide-react";

const HowItWorksSection = () => {
  const steps = [
    {
      icon: <Upload className="h-8 w-8" />,
      title: "Upload your Datasets",
      description: "Upload one or more CSV or Excel files. Our AI cleans your unformatted data into a single, analysis-ready dataset."
    },
    {
      icon: <BookOpen className="h-8 w-8" />,
      title: "Input Parameters",
      description: "Choose a regression model, map your cleaned dataset’s columns to the regression variables, and select the graphs or diagrams you want to generate."
    },
    {
      icon: <FileText className="h-8 w-8" />,
      title: "Generate & Download",
      description: "Our AI creates your econometrics files, complete with proper formatting, explanatory notes, and comments—ready to run."
    }
  ];

  return (
    <section id="how-it-works" className="py-20">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16 fadeIn">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">How It Works</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Generate high-quality Econometric Reports in just three simple steps.
          </p>
        </div>
        
        <div className="flex flex-col md:flex-row md:justify-between gap-8">
          {steps.map((step, index) => (
            <div key={index} className="flex-1 relative fadeIn">
              <div className="bg-white rounded-xl p-8 border border-gray-100 shadow-sm h-full flex flex-col items-center text-center">
                <div className="h-16 w-16 rounded-full bg-primary flex items-center justify-center text-white mb-6">
                  {step.icon}
                </div>
                <h3 className="text-xl font-semibold mb-3">{step.title}</h3>
                <p className="text-gray-600">{step.description}</p>
              </div>
              
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-1/2 left-full transform -translate-y-1/2 w-12 h-1 bg-gray-200 z-0">
                  <div className="absolute right-0 top-1/2 transform translate-x-1/2 -translate-y-1/2 h-3 w-3 rounded-full bg-primary"></div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorksSection;
