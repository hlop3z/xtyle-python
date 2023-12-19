/* Library */
import Actions from "./app/actions.ts";
import Directives from "./app/directives.ts";
import Globals from "./app/globals.ts";
import Models from "./app/models.ts";
import Init from "./app/init.ts";
import Router from "./app/router.ts";
import Store from "./app/store.ts";

/* Components */
export * from "./components/index.ts";

/* Style-Sheets */ //{{ styles }}

/* Plugin Install */
export function install(/* self, option */) {
  return {
    init: Init,
    actions: Actions,
    directives: Directives,
    globals: Globals,
    models: Models,
    router: Router,
    store: Store,
  };
}
