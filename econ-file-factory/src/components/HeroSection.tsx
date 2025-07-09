
import React from "react";
import { Button } from "@/components/ui/button";
import { GraduationCap, FileSearch } from "lucide-react";
import { Link } from "react-router-dom";

const HeroSection = () => {
  return (
    <section className="py-20 md:py-28">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row items-center">
          <div className="md:w-1/2 md:pr-12 mb-12 md:mb-0">
            <div className="fadeIn">
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight mb-6">
                Econometrics Assignments, <span className="text-primary">Made Easy</span>
              </h1>
              <p className="text-xl text-gray-600 mb-8">
                Perfect econometrics analysis reports, clean gathered data sets, and easily generate Stata .do files with just a few clicks.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Button size="lg" className="px-8"><Link to="/upload">Start Generating Files</Link></Button>
                <Button size="lg" variant="outline" className="px-8">
                  Watch Demo
                </Button>
              </div>
              <div className="mt-8 flex items-center text-sm text-gray-500">
                <GraduationCap className="h-5 w-5 mr-2 text-primary" />
                <span>Trusted by 1+ economics students across 1+ university</span>
              </div>
            </div>
          </div>
          <div className="md:w-1/2 fadeIn">
            <div className="relative">
              <div className="bg-gradient-to-tr from-accent to-secondary rounded-xl shadow-lg p-6">
                <div className="bg-white rounded-lg shadow-md p-4">
                  <div className="flex items-center mb-4">
                    <FileSearch className="h-5 w-5 text-primary mr-2" />
                    <h3 className="font-medium">Econometric Data Analysis</h3>
                  </div>
                  <div className="bg-gray-50 rounded-md p-3 mb-3">
                    <div className="h-2 bg-primary/20 rounded-full w-3/4"></div>
                    <div className="h-2 bg-secondary/20 rounded-full w-1/2 mt-2"></div>
                    <div className="h-2 bg-primary/20 rounded-full w-5/6 mt-2"></div>
                  </div>
                  <div className="bg-gray-50 rounded-md p-3">
                    <div className="grid grid-cols-3 gap-2">
                      <div className="h-10 bg-primary/10 rounded"></div>
                      <div className="h-10 bg-secondary/10 rounded"></div>
                      <div className="h-10 bg-accent/10 rounded"></div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="absolute -bottom-4 -right-4 bg-white p-3 rounded-lg shadow-lg border border-gray-100">
                <div className="flex items-center">
                  <div className="h-3 w-3 bg-green-500 rounded-full mr-2"></div>
                  <span className="text-xs font-medium">Report Complete</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
