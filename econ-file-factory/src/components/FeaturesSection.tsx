
import React from "react";
import { FileText, GraduationCap, Wrench, Laptop } from "lucide-react";

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

const FeatureCard = ({ icon, title, description }: FeatureCardProps) => {
  return (
    <div className="p-6 bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
      <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center text-primary mb-5">
        {icon}
      </div>
      <h3 className="text-xl font-semibold mb-3">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
};

const FeaturesSection = () => {
  const features = [
    {
      icon: <FileText className="h-6 w-6" />,
      title: "Ready-to-Submit Files",
      description: "Generate professional econometric reports using your own datasets. Export cleaned CSVs and Stata .do files that meet academic standards."
    },
    {
      icon: <GraduationCap className="h-6 w-6" />,
      title: "Course-Specific Regressions",
      description: "Templates for all major regression models covered in your econometrics courses—streamlined and ready to run."
    },
    {
      icon: <Wrench className="h-6 w-6" />,
      title: "Data Analysis Tools",
      description: "Map CSV data to regression variables, run regressions, and generate both graphs and diagrams to visualise your results."


    },
    {
      icon: <Laptop className="h-6 w-6" />,
      title: "Learning Resources",
      description: "Each generated file includes explanatory notes and comments to help you understand the econometric concepts behind the analysis."
    }
  ];

  return (
    <section id="features" className="py-20 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16 fadeIn">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Features Designed for Economics Students</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Our platform offers specialised tools that make econometrics assignments easier to complete and understand.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 fadeIn">
          {features.map((feature, index) => (
            <FeatureCard 
              key={index}
              icon={feature.icon}
              title={feature.title}
              description={feature.description}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;
