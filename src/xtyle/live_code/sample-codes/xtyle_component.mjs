import { writeFile, mkdir, readdir } from "fs/promises";
import fs from "fs";
import path from "path";

const pkg = JSON.parse(await fs.promises.readFile("./package.json", "utf-8"));
const packageName = pkg.name.replace(/-/g, "_");
const componentName = process.argv[2];

const titleCase = (text) => {
  const _text = text.replace(/-/g, " "); // Use a global replace to replace all occurrences
  return _text
    .toLowerCase()
    .split(" ")
    .map((e) => e.charAt(0).toUpperCase() + e.slice(1))
    .join("");
};

if (!componentName) {
  console.error("Error: Please provide a component name.");
  process.exit(1);
}

const className = titleCase(componentName);
const mainFolderPath = "./src/components/";
const destinationFolder = path.join(mainFolderPath, className);

async function generateFiles(folderPath, fileData) {
  try {
    // Ensure the destination folder exists
    await mkdir(folderPath, { recursive: true });

    // Extra Code
    const themeName = `${packageName}__`;

    // Write files
    await Promise.all(
      Object.entries(fileData).map(async ([fileName, fileContent]) => {
        let content = fileContent.trim();
        const filePath = path.join(folderPath, fileName);
        if (fileName === "index.tsx") {
          content = `const $NAME = "${themeName}${className}";\n\n${fileContent.trim()}`;
        }
        if (fileName === "style.scss") {
          content = `$NAME: "${themeName}${className}";\n\n${
            fileContent.trim() || ""
          }`;
        }
        await writeFile(filePath, content, "utf-8");
        console.log(`File created: ${filePath}`);
      })
    );

    // List all folders in the components directory
    const componentFolders = await readdir(mainFolderPath, {
      withFileTypes: true,
    });

    // Create a list of export statements for each component
    const exportStatements = componentFolders
      .filter((dirent) => dirent.isDirectory())
      .map((dirent) => {
        const name = dirent.name;
        return `export { default as ${name} } from "./${name}/index.tsx";`;
      });

    // Create an index.tsx file in the components folder with the export statements
    const indexPath = path.join(mainFolderPath, "index.ts");
    await writeFile(indexPath, exportStatements.join("\n"), "utf-8");
    console.log(`File created: ${indexPath}`);
  } catch (error) {
    console.error("Error generating files:", error);
  }
}
function isDirectoryExists(directoryPath) {
  try {
    // Attempt to get the stats of the directory
    const stats = fs.statSync(directoryPath);

    // Check if it's a directory
    return stats.isDirectory();
  } catch (error) {
    // Handle the error (directory does not exist)
    return false;
  }
}

const sample = {};

sample["index.tsx"] = `
import "./style.scss";

export default function ${className}(props) {
  return (
    <div x-html {...props} class={[$NAME, props.class]}>
      {props.children}
    </div>
  );
}
`;

sample["style.scss"] = `
.#{$NAME} {
  color: red;
}
`;

sample["props.tsx"] = `
type Props = {
  class?: string | any[] | Record<string, boolean> | any;
  style?: string | any[] | Record<string, string> | any;
  children?: any;
};

export default Props;
/**
  ---------------
  @ Cheat-Sheet
  ---------------
  
  // Primitives
  void
  null
  bigint
  
  // Basic types
  any
  boolean
  number
  string
  
  // Arrays
  string[]        
  Array<string>  
  
  // Tuples
  [string, number]
  
  // Unions
  string | null | undefined 
  
**/
`;

sample["docs.tsx"] = `
/**
 * ${className} - ${packageName} Component.
 *
 * @component
 *
 * @param {Props} props - The props object containing the following attributes:
 * @param {any} [props.class] - The CSS classes to apply to the component.
 * @param {any} [props.style] - The inline CSS styles to apply to the component.
 * @param {any} [props.children] - Child elements or content to render inside the component.
 *
 * @returns {JSX.Element} The rendered Component.
 *
 * @example
 *
 * // Render the component with default class and style.
 * <${packageName}.${className}></${packageName}.${className}>
 *
 * // Render the component with custom class and style.
 * <${packageName}.${className} class="custom-class" style="color: red;"></${packageName}.${className}>
 */
`;

// Example usage:
if (isDirectoryExists(destinationFolder)) {
  console.log(`Component { ${className} } already exists.`);
} else {
  generateFiles(destinationFolder, sample);
}
