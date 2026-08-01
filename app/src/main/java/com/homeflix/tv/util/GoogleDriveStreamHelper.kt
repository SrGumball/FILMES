package com.homeflix.tv.util

/**
 * Utilitário para conversão e manipulação de mídias e vídeos hospedados no Google Drive
 * para execução perfeita no ExoPlayer no Android TV.
 */
object GoogleDriveStreamHelper {

    const val DEFAULT_FOLDER_ID = "1Cne2Ci8boM9TQ19DAoGY-yhCbt07XGzm"
    const val DEFAULT_FOLDER_URL = "https://drive.google.com/drive/u/3/folders/1Cne2Ci8boM9TQ19DAoGY-yhCbt07XGzm"

    /**
     * Extrai o ID do arquivo ou pasta do Google Drive a partir da URL fornecida.
     */
    fun extractDriveId(urlOrId: String): String {
        if (urlOrId.isBlank()) return DEFAULT_FOLDER_ID
        if (urlOrId.length == 33 && !urlOrId.contains("/")) return urlOrId
        
        val folderRegex = Regex("""folders/([a-zA-Z0-9_-]{25,50})""")
        val fileRegex = Regex("""/d/([a-zA-Z0-9_-]{25,50})""")
        val idRegex = Regex("""id=([a-zA-Z0-9_-]{25,50})""")

        folderRegex.find(urlOrId)?.groupValues?.get(1)?.let { return it }
        fileRegex.find(urlOrId)?.groupValues?.get(1)?.let { return it }
        idRegex.find(urlOrId)?.groupValues?.get(1)?.let { return it }

        return urlOrId.trim()
    }

    /**
     * Retorna a lista completa de URLs de streaming direto do Google Drive para fallback no ExoPlayer.
     */
    fun getStreamUrls(urlOrId: String): List<String> {
        val cleanId = extractDriveId(urlOrId)
        return listOf(
            "https://drive.google.com/uc?export=download&confirm=t&id=$cleanId",
            "https://drive.google.com/uc?export=download&id=$cleanId",
            "https://docs.google.com/uc?export=download&confirm=t&id=$cleanId",
            "https://drive.usercontent.google.com/download?id=$cleanId&export=download&confirm=t"
        )
    }

    /**
     * Converte o ID de um arquivo do Google Drive em URL de streaming direto para o ExoPlayer.
     */
    fun buildDirectStreamUrl(fileId: String): String {
        return getStreamUrls(fileId).first()
    }

    /**
     * Converte a URL para visualização web/embed.
     */
    fun buildEmbedUrl(fileId: String): String {
        val cleanId = extractDriveId(fileId)
        return "https://drive.google.com/file/d/$cleanId/preview"
    }
}
