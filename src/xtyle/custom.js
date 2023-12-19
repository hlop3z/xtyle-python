/*
var JSX = (code, jsxFactory = "h") => {
  try {
    return Babel.transform(code, { presets: ["react"] }).code.replace(
      /\/\*\#\_\_PURE\_\_\*\/\s*React\.createElement/g,
      jsxFactory
    );
  } catch (e) {
    return code;
  }
};
*/

var prettyCode = (function () {
  const FORMAT = {
    graphql(code) {
      return prettier.format(code, {
        parser: "graphql",
        plugins: prettierPlugins,
      });
    },
    javascript(code) {
      try {
        return prettier.format(code, {
          parser: "babel",
          plugins: prettierPlugins,
        });
      } catch (e) {
        return code;
      }
    },
    css(code) {
      return prettier.format(code, {
        parser: "css",
        plugins: prettierPlugins,
      });
    },
    scss(code) {
      return prettier.format(code, {
        parser: "scss",
        plugins: prettierPlugins,
      });
    },
    json(code) {
      let value = code;
      try {
        value = JSON.stringify(JSON.parse(value), null, "\t");
      } catch (e) {
        //pass
      }
      return value;
    },
  };

  const prettyCode = (content, language) => {
    const lang = language || "javascript";
    switch (lang) {
      case "javascript":
      case "typescript":
        content = FORMAT.javascript(content);
        break;
      case "css":
        content = FORMAT.css(content);
        break;
      case "scss":
        content = FORMAT.scss(content);
        break;
      case "json":
        content = FORMAT.json(content);
        break;
      case "graphql":
        content = FORMAT.graphql(content);
        break;
    }
    return content;
  };

  return prettyCode;
})();
