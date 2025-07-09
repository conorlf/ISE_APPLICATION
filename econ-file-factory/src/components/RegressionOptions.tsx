
import React from 'react';
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Form, FormField, FormItem, FormLabel, FormControl, FormDescription, FormMessage } from "@/components/ui/form";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";

interface RegressionOptionsProps {
  headers: string[];
  headerMapping: Record<string, string>;
  onOptionsComplete: (options: any) => void;
}

const regressionSchema = z.object({
  type: z.enum(["OLS", "IV", "FixedEffects", "Logit", "Probit"]),
  robustSE: z.boolean().default(false),
  clustering: z.boolean().default(false),
  clusterVariable: z.string().optional(),
  timeTrends: z.boolean().default(false),
  interactions: z.boolean().default(false),
  scatterPlot: z.boolean().default(false),
  barChart: z.boolean().default(false),
  fixedEffectsVariables: z.array(z.string()).default([]),
});

type RegressionFormValues = z.infer<typeof regressionSchema>;

const RegressionOptions = ({ headers, headerMapping, onOptionsComplete }: RegressionOptionsProps) => {
  const form = useForm<RegressionFormValues>({
    resolver: zodResolver(regressionSchema),
    defaultValues: {
      type: "OLS",
      robustSE: false,
      clustering: false,
      timeTrends: false,
      interactions: false,
      fixedEffectsVariables: [],
    },
  });

  const watchClustering = form.watch("clustering");
  const watchType = form.watch("type");
  
  // Filter headers based on mapping for relevant selections
  const idVariables = headers.filter(header => headerMapping[header] === "id" || headerMapping[header] === "fixed_effect");
  const timeVariables = headers.filter(header => headerMapping[header] === "time");
  const allVariables = headers.filter(header => headerMapping[header] !== "ignore");

  const onSubmit = (data: RegressionFormValues) => {
    onOptionsComplete(data);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">Regression Options</h2>
        <p className="text-gray-500 mb-4">
          Configure the settings for your regression analysis
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <div className="space-y-4">
            <FormField
              control={form.control}
              name="type"
              render={({ field }) => (
                <FormItem className="space-y-3">
                  <FormLabel>Regression Type</FormLabel>
                  <FormControl>
                    <RadioGroup
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                      className="flex flex-col space-y-1"
                    >
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="OLS" id="r1" />
                        <Label htmlFor="r1">OLS (Ordinary Least Squares)</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="IV" id="r2" />
                        <Label htmlFor="r2">IV (Instrumental Variables)</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="FixedEffects" id="r3" />
                        <Label htmlFor="r3">Fixed Effects</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="Logit" id="r4" />
                        <Label htmlFor="r4">Logit</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="Probit" id="r5" />
                        <Label htmlFor="r5">Probit</Label>
                      </div>
                    </RadioGroup>
                  </FormControl>
                </FormItem>
              )}
            />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <FormField
                control={form.control}
                name="robustSE"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                    <FormControl>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                    <div className="space-y-1 leading-none">
                      <FormLabel>
                        Use Robust Standard Errors
                      </FormLabel>
                      <FormDescription>
                        Account for heteroskedasticity in your data
                      </FormDescription>
                    </div>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="clustering"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                    <FormControl>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                    <div className="space-y-1 leading-none">
                      <FormLabel>
                        Cluster Standard Errors
                      </FormLabel>
                      <FormDescription>
                        Account for correlations within groups
                      </FormDescription>
                    </div>
                  </FormItem>
                )}
              />
            </div>

            {watchClustering && (
              <FormField
                control={form.control}
                name="clusterVariable"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Cluster Variable</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select cluster variable" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {idVariables.map((variable) => (
                          <SelectItem key={variable} value={variable}>
                            {variable}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      Variable to use for clustered standard errors
                    </FormDescription>
                  </FormItem>
                )}
              />
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <FormField
                control={form.control}
                name="timeTrends"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                    <FormControl>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                    <div className="space-y-1 leading-none">
                      <FormLabel>
                        Include Time Trends
                      </FormLabel>
                      <FormDescription>
                        Control for time-varying trends in your data
                      </FormDescription>
                    </div>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="interactions"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                    <FormControl>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                    <div className="space-y-1 leading-none">
                      <FormLabel>
                        Include Interactions
                      </FormLabel>
                      <FormDescription>
                        Create interaction terms between independent variables
                      </FormDescription>
                    </div>
                  </FormItem>
                )}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <FormField
                control={form.control}
                name="barChart"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                    <FormControl>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                    <div className="space-y-1 leading-none">
                      <FormLabel>
                        Generate Bar Chart
                      </FormLabel>
                      <FormDescription>
                        Compare the values of selected variables using a bar chart.
                      </FormDescription>
                    </div>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="scatterPlot"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                    <FormControl>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                    <div className="space-y-1 leading-none">
                      <FormLabel>
                        Generate Scatterplot
                      </FormLabel>
                      <FormDescription>
                        Plot one variable against another to explore their relationship.
                      </FormDescription>
                    </div>
                  </FormItem>
                )}
              />
            </div>

            {watchType === "FixedEffects" && (
              <FormField
                control={form.control}
                name="fixedEffectsVariables"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Fixed Effects Variables</FormLabel>
                    <FormDescription>
                      Select variables to use for fixed effects
                    </FormDescription>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
                      {idVariables.map((variable) => (
                        <div key={variable} className="flex items-center space-x-2">
                          <Checkbox
                            id={`fe-${variable}`}
                            checked={field.value?.includes(variable)}
                            onCheckedChange={(checked) => {
                              if (checked) {
                                field.onChange([...field.value, variable]);
                              } else {
                                field.onChange(
                                  field.value.filter((v) => v !== variable)
                                );
                              }
                            }}
                          />
                          <label
                            htmlFor={`fe-${variable}`}
                            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                          >
                            {variable}
                          </label>
                        </div>
                      ))}
                    </div>
                  </FormItem>
                )}
              />
            )}
          </div>
          

          <Button type="submit" className="w-full md:w-auto">
            Save Regression Options & Continue
          </Button>
        </form>
      </Form>
    </div>
  );
};

export default RegressionOptions;
