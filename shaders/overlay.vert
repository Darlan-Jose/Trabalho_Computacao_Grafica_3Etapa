#version 330 core
out vec2 uv;
void main() {
    vec2 vertices[3] = vec2[3](vec2(-1,-1),vec2(3,-1),vec2(-1,3));
    vec2 position = vertices[gl_VertexID];
    uv = position * 0.5 + 0.5;
    gl_Position = vec4(position,0,1);
}
