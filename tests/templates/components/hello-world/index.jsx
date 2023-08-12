export default function Component(props) {
  const className = "icon";
  return (
    <div
      class={[className, props.class]}
      {...props}
      x-html
      on-click={() => console.log("hello world")}
      x-demo
    >
      Hello World
    </div>
  );
}
