import React from "react";
import {
  InstructionsCard,
  InstructionsCardHeader,
  InstructionsCardTitle,
  InstructionsCardDescription,
  InstructionsCardContent
} from "@/components/ui/instructionCards";

const InstructionsCardComponent: React.FC = () => (
    <InstructionsCard className="mt-8">
          <InstructionsCardHeader>
            <InstructionsCardTitle>How to Use the StataGo Generator</InstructionsCardTitle>
            <InstructionsCardDescription>
              Follow these steps to generate custom Stata code from your Excel data
            </InstructionsCardDescription>
          </InstructionsCardHeader>
          <InstructionsCardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <h3 className="font-medium text-lg">1. Upload Your Data</h3>
                <p className="text-sm text-gray-600">
                  Start by uploading your Excel (.xlsx) file containing the data you want to analyze.
                </p>
              </div>
              <div className="space-y-2">
                <h3 className="font-medium text-lg">2. Preview Data</h3>
                <p className="text-sm text-gray-600">
                  Review your data and select the correct sheet if your file contains multiple worksheets.
                </p>
              </div>
              <div className="space-y-2">
                <h3 className="font-medium text-lg">3. Map Variables</h3>
                <p className="text-sm text-gray-600">
                  Assign roles to each column (dependent variables, independent variables, etc.) and add transformations if needed.
                </p>
              </div>
              <div className="space-y-2">
                <h3 className="font-medium text-lg">4. Configure Regression</h3>
                <p className="text-sm text-gray-600">
                  Select regression type, standard error settings, fixed effects, and other options for your analysis.
                </p>
              </div>
            </div>
            <div className="pt-2">
              <h3 className="font-medium text-lg">5. Generate Files</h3>
              <p className="text-sm text-gray-600">
                Get a ready-to-use Stata .do file and a cleaned Excel file based on your specifications.
              </p>
            </div>
          </InstructionsCardContent>
        </InstructionsCard>
);

export default InstructionsCardComponent;
