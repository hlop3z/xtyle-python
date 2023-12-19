import fs from "fs";
import path from "path";
import zlib from "zlib";

const pkg = JSON.parse(fs.readFileSync("./package.json", "utf-8"));
const packageName = pkg.name.replace(/-/g, "_");

/**
 * @Declarations
 */
export const removeSemiColon = (value) => {
  value = value.trim();
  return value.endsWith(";") ? value.slice(0, -1) : value;
};

function parseType(typeString) {
  // Remove single-line comments
  const content = typeString.replace(/\/\/.*$/gm, "");

  // Remove multi-line comments
  const contentWithoutComments = content.replace(
    /\/\*[\s\S]*?\*\/|\/\/.*/g,
    ""
  );

  // Replace export statement and type declaration
  const propsContent = contentWithoutComments
    .replace(/export default Props;/, "")
    .replace(/type Props =/, "")
    .trim();

  return propsContent || "any";
}

export function createDeclaration(name, props, docs, esmodule) {
  const esmCode = esmodule ? "export const " : "";
  const readDocs = docs ? docs.trim() : "";
  if (!props) {
    return "";
  }
  const propsText = parseType(props);
  return `${readDocs}\n${esmCode}${name}: ${propsText}`.trim();
}

function processDeclaration(subfolderPath) {
  const name = path.basename(subfolderPath);
  let props = "";
  let docs = "";

  const propsFilePath = path.join(subfolderPath, "props.tsx");
  const docsFilePath = path.join(subfolderPath, "docs.tsx");

  if (fs.existsSync(propsFilePath)) {
    props = fs.readFileSync(propsFilePath, "utf8");
  }

  if (fs.existsSync(docsFilePath)) {
    docs = fs.readFileSync(docsFilePath, "utf8");
  }

  return createDeclaration(name, props, docs);
}

function getSubfolders(folderPath) {
  return fs
    .readdirSync(folderPath, { withFileTypes: true })
    .filter((dirent) => dirent.isDirectory())
    .map((dirent) => dirent.name);
}

function createDeclarations(srcFolderPath, outputDir) {
  const componentsFolderPath = path.join(srcFolderPath, "components");
  const mainDocsPath = `${srcFolderPath}/app/docs.ts`;
  const subfolders = getSubfolders(componentsFolderPath);
  const subfolderObjects = [];

  subfolders.forEach((subfolder) => {
    const subfolderPath = path.join(componentsFolderPath, subfolder);
    const subfolderObject = processDeclaration(subfolderPath);
    subfolderObjects.push(subfolderObject);
  });

  const allDeclarations = subfolderObjects.join("\n\n").trim();

  let mainDocs = "";
  if (fs.existsSync(mainDocsPath)) {
    mainDocs = fs.readFileSync(mainDocsPath, "utf8");
  }
  const declarations = `${mainDocs}\ndeclare const ${packageName}: {\n${allDeclarations}\n};`;

  fs.writeFileSync(`${outputDir}/index.d.ts`, declarations);
}

/**
 * @GZip
 */
function gzipJsonFiles(filesToInclude, outputFilename) {
  const output = fs.createWriteStream(outputFilename);
  const gzipStream = zlib.createGzip();

  gzipStream.pipe(output);

  const jsonData = {
    name: packageName,
    package: pkg,
  };

  filesToInclude.forEach((filename) => {
    let content = "";
    try {
      const filePath = `dist/${filename}`;
      if (fs.existsSync(filePath)) {
        content = fs.readFileSync(filePath, "utf8");
      }
    } catch (e) {}
    if (filename === "index.min.js") {
      jsonData["javascript"] = content;
    } else if (filename === "style.css") {
      jsonData["style"] = content;
    } else if (filename === "index.d.ts") {
      jsonData["declarations"] = content;
    }
  });

  const outputString = JSON.stringify(jsonData, null, 4);
  const jsonBuffer = Buffer.from(outputString);

  gzipStream.write(jsonBuffer);
  gzipStream.end();
}

function packageXtylePlugin() {
  // Build Declarations
  const distFolderPath = "./dist";
  const mainFolderPath = "./src";
  createDeclarations(mainFolderPath, distFolderPath);

  // Build GZip
  const filesToInclude = ["index.min.js", "index.d.ts", "style.css"];
  const outputFilename = "plugin.json.gz";
  gzipJsonFiles(filesToInclude, `${distFolderPath}/${outputFilename}`);
}

packageXtylePlugin();
