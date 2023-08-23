const generator = require("@babel/generator");
const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;
const t = require("@babel/types");
const fs = require("fs/promises");
const path = require("path");

const patchCancellablePromise = async () => {
  const src = path.resolve(process.cwd(), "client/core/CancelablePromise.ts");

  let content = await fs.readFile(src, { encoding: "utf-8" });
  content = content.replaceAll("#", "");

  const ast = parser.parse(content, { sourceType: "module", plugins: ["typescript"] });
  traverse(ast, {
    ClassMethod: (current) => {
      if (t.isIdentifier(current.node.key, { name: "isCancelled" })) {
        current.remove();
        current.skip();
      }
    },
  });

  const { code } = new generator.CodeGenerator(ast).generate();
  await fs.writeFile(src, code, "utf-8");
};

patchCancellablePromise().catch((error) => {
  console.error("An error occurred:", error);
});
