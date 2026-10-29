#version 330 core
layout(location = 0) in vec3 vertexPosition;
layout(location = 1) in vec3 vertexNormal;
layout(location = 2) in vec2 vertexUV;
uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform mat4 lightMatrix;
uniform mat3 normalMatrix;
out vec3 worldPosition;
out vec3 worldNormal;
out vec2 uv;
out vec4 lightPosition;
void main() {
    vec4 world = modelMatrix * vec4(vertexPosition, 1.0);
    worldPosition = world.xyz;
    worldNormal = normalize(normalMatrix * vertexNormal);
    uv = vertexUV;
    lightPosition = lightMatrix * world;
    gl_Position = projectionMatrix * viewMatrix * world;
}
