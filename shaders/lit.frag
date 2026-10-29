#version 330 core
in vec3 worldPosition;
in vec3 worldNormal;
in vec2 uv;
in vec4 lightPosition;
out vec4 fragColor;
uniform vec3 baseColor;
uniform vec3 lightDirection;
uniform vec3 cameraPosition;
uniform sampler2D colorTexture;
uniform sampler2D shadowMap;
uniform bool useTexture;
uniform bool shadowsEnabled;
uniform bool proceduralEnabled;
uniform vec2 uvRepeat;
uniform float specularStrength;
uniform float shininess;
uniform float emission;

float shadowVisibility(vec3 normal, vec3 towardLight) {
    vec3 p = lightPosition.xyz / lightPosition.w * 0.5 + 0.5;
    if (!shadowsEnabled || p.z > 1.0 || p.z < 0.0 ||
        p.x < 0.0 || p.x > 1.0 || p.y < 0.0 || p.y > 1.0) return 1.0;
    float resolutionScale = 2048.0 / float(textureSize(shadowMap, 0).x);
    float bias = max(0.0035 * (1.0 - dot(normal, towardLight)), 0.0010) * resolutionScale;
    vec2 texel = 1.0 / vec2(textureSize(shadowMap, 0));
    float visible = 0.0;
    // PCF: média de nove comparações, suavizando a borda do shadow map.
    for (int x = -1; x <= 1; ++x)
        for (int y = -1; y <= 1; ++y) {
            float depth = texture(shadowMap, p.xy + vec2(x,y)*texel).r;
            visible += p.z - bias <= depth ? 1.0 : 0.0;
        }
    return visible / 9.0;
}

void main() {
    vec3 color = baseColor;
    if (useTexture) color *= texture(colorTexture, uv * uvRepeat).rgb;
    // Recurso adicional: faixas de segurança calculadas no fragment shader.
    if (proceduralEnabled) {
        float stripe = step(0.48, fract((uv.x + uv.y) * 12.0));
        color = mix(vec3(0.035,0.055,0.065), baseColor, stripe);
    }
    vec3 N = normalize(worldNormal);
    vec3 L = normalize(-lightDirection);
    vec3 V = normalize(cameraPosition - worldPosition);
    vec3 H = normalize(L + V);
    float diffuse = max(dot(N, L), 0.0);
    float specular = diffuse > 0.0 ? pow(max(dot(N,H), 0.0), shininess) * specularStrength : 0.0;
    float visibility = shadowVisibility(N,L);
    // Ambiente continua presente na sombra; só a luz direta é ocluída.
    vec3 lit = color * vec3(0.27,0.31,0.36) + visibility *
               (color * vec3(0.94,0.87,0.73) * diffuse + vec3(specular));
    lit = mix(lit, color, clamp(emission, 0.0, 1.0));
    float fog = smoothstep(28.0, 65.0, length(cameraPosition-worldPosition));
    fragColor = vec4(mix(lit, vec3(0.055,0.09,0.13), fog), 1.0);
}
