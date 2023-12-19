// @ts-nocheck
import * as Plugin from "./index.ts";

/**
 * @Register <Plugin>
 */
xtyle.use(Plugin);

/**
 * @Router
 */
const router = {
  history: false,
  baseURL: null,
};

/**
 * @DEMO
 */
function Demo() {
  const allLinks = {
    docs: "https://hlop3z.github.io/xtyle/",
    libs: "https://github.com/hlop3z/xtyle-template/",
  };
  return h(
    "div",
    {
      style:
        "height: 80vh; width: 100%; text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center;",
    },
    h(
      "h1",
      { style: "font-family: 'Arial', sans-serif; color: #333;" },
      "Welcome To Xtyle Plugins"
    ),
    h(
      "div",
      null,
      h(
        "a",
        {
          href: allLinks.docs,
          target: "_blank",
          style:
            "text-decoration: none; padding: 10px 20px; background-color: #4CAF50; color: #fff; border-radius: 5px; margin: 0 8px;",
        },
        "Read Documentation"
      ),
      h(
        "a",
        {
          href: allLinks.libs,
          target: "_blank",
          style:
            "text-decoration: none; padding: 10px 20px; background-color: #007BFF; color: #fff; border-radius: 5px;",
        },
        "Xtyle Library Template (PNPM + TypeScript)"
      )
    )
  );
}

/**
 * @Render
 */
xtyle.init(Demo, document.body, router);

/**
 * @Preview
 */

/* Globals */
console.log("Globals: ", xtyle.global);

/* Store */
console.log("Store: ", xtyle.store);

/* Routes */
console.log("Routes: ", Object.keys(xtyle.router.routes));

/* Directives Keys */
console.log("Directives: ", Object.keys(xtyle.allDirectives));
