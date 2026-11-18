import { registerRoot, Composition } from "remotion";
import { Clip, clipSchema } from "./Clip";

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="Clip"
      component={Clip}
      width={1280}
      height={720}
      fps={30}
      durationInFrames={3000}
      defaultProps={{}}
    />
  </>
);

registerRoot(RemotionRoot);
