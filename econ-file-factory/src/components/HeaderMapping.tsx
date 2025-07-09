
import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Form, FormField, FormItem, FormLabel, FormControl, FormDescription, FormMessage } from "@/components/ui/form";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";

interface HeaderMappingProps {
  headers: string[];
  onMappingComplete: (mapping: Record<string, string>) => void;
}

const VARIABLE_ROLES = [
  { value: "dependent", label: "Dependent Variable" },
  { value: "independent", label: "Independent Variable" },
  { value: "control", label: "Control Variable" },
  { value: "fixed_effect", label: "Fixed Effect" },
  { value: "time", label: "Time Variable" },
  { value: "id", label: "ID Variable" },
  { value: "instrument", label: "Instrumental Variable" },
  { value: "weight", label: "Weight Variable" },
  { value: "cluster", label: "Cluster Variable" },
  { value: "ignore", label: "Ignore" }
];

const HeaderMapping = ({ headers, onMappingComplete }: HeaderMappingProps) => {
  const [mapping, setMapping] = useState<Record<string, string>>({});

  // Set up form schema based on headers
  const formSchema = z.object(
    headers.reduce((acc: any, header) => {
      acc[header] = z.string().optional();
      return acc;
    }, {})
  );

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: headers.reduce((acc: any, header) => {
      acc[header] = "ignore"; // Default all to ignore
      return acc;
    }, {}),
  });

  const onSubmit = (values: z.infer<typeof formSchema>) => {
    onMappingComplete(values);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">Map Your Variables</h2>
        <p className="text-gray-500 mb-4">
          Assign each column to a specific role for your regression analysis
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {headers.map((header) => (
              <FormField
                key={header}
                control={form.control}
                name={header}
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{header}</FormLabel>
                    <Select 
                      onValueChange={field.onChange} 
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select role" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {VARIABLE_ROLES.map((role) => (
                          <SelectItem key={role.value} value={role.value}>
                            {role.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      Choose the role for column "{header}"
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            ))}
          </div>
          
          <Button type="submit" className="w-full md:w-auto">
            Save Mapping & Continue
          </Button>
        </form>
      </Form>
    </div>
  );
};

export default HeaderMapping;
